"""
Claude API content enhancer for generating improved summaries and takeaways.

This module uses Claude to enhance story content with:
- Better executive summaries (from search snippets)
- Story-specific actionable takeaways
- Extracted compliance deadlines
- Extracted penalty/fine amounts
"""
import os
import re
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Try to import anthropic - will fail gracefully if not installed
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from .news_collector import NewsStory
from .config import ALL_JURISDICTIONS


def load_api_key() -> Optional[str]:
    """
    Load Claude API key from config file or environment.

    Checks in order:
    1. api_key.txt file in project root
    2. ANTHROPIC_API_KEY environment variable

    Returns:
        API key string or None if not found
    """
    # Check for api_key.txt file
    project_root = Path(__file__).parent.parent
    key_file = project_root / 'api_key.txt'

    if key_file.exists():
        key = key_file.read_text().strip()
        if key and not key.startswith('#'):
            return key

    # Fall back to environment variable
    return os.environ.get('ANTHROPIC_API_KEY')


class ContentEnhancer:
    """Enhances story content using Claude API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the content enhancer.

        Args:
            api_key: Optional API key. If not provided, will try to load from config.
        """
        self.api_key = api_key or load_api_key()
        self.client = None
        self.enabled = False

        if not ANTHROPIC_AVAILABLE:
            print("  [ContentEnhancer] anthropic package not installed. Run: pip install anthropic")
            return

        if not self.api_key:
            print("  [ContentEnhancer] No API key found. Create api_key.txt with your Anthropic API key.")
            return

        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.enabled = True
        except Exception as e:
            print(f"  [ContentEnhancer] Failed to initialize: {e}")

    def enhance_story(self, story: NewsStory) -> NewsStory:
        """
        Enhance a story with better summary and takeaways.

        Args:
            story: NewsStory object with basic info

        Returns:
            Enhanced NewsStory with improved summary and takeaways
        """
        if not self.enabled:
            return story

        jur_name = ALL_JURISDICTIONS.get(story.jurisdiction, {}).get('name', story.jurisdiction)
        categories = ', '.join(getattr(story, 'categories', [])[:3]) or 'Legal/Regulatory'

        prompt = f"""You are a legal analyst writing for in-house counsel at a global SaaS company.
Analyze this legal news story and provide enhanced content.

STORY DETAILS:
- Title: {story.title}
- Jurisdiction: {jur_name}
- Categories: {categories}
- Original snippet: {story.summary or story.snippet}
- Source: {story.source}
- URL: {story.url}

Provide your analysis in the following JSON format:
{{
    "summary": "A 2-3 sentence executive summary of what happened and why it matters. Be specific about the regulation/law/enforcement action. Use plain language, no jargon.",
    "takeaways": [
        "First specific, actionable takeaway for a tech company",
        "Second specific, actionable takeaway",
        "Third specific, actionable takeaway (if applicable)"
    ],
    "deadline": "YYYY-MM-DD format if a compliance deadline is mentioned, otherwise null",
    "deadline_description": "Brief description of what the deadline is for, or null",
    "penalty_amount": "Extracted fine/penalty amount with currency if mentioned, otherwise null",
    "is_ai_related": true/false based on whether this story involves AI/ML regulation
}}

GUIDELINES:
- Summary should explain WHAT happened, WHO is affected, and WHY it matters
- Takeaways must be specific and actionable (e.g., "Review privacy notices for Australian users" not "Monitor developments")
- Extract any specific dates mentioned as compliance deadlines
- Note penalty amounts to help prioritize enforcement stories
- Flag AI-related stories for the AI Regulatory Tracker

Respond ONLY with the JSON object, no other text."""

        try:
            response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            response_text = response.content[0].text.strip()

            # Try to extract JSON from response
            try:
                # Handle potential markdown code blocks
                if response_text.startswith('```'):
                    response_text = re.sub(r'^```json?\n?', '', response_text)
                    response_text = re.sub(r'\n?```$', '', response_text)

                data = json.loads(response_text)

                # Update story with enhanced content
                if data.get('summary'):
                    story.enhanced_summary = data['summary']

                if data.get('takeaways'):
                    story.enhanced_takeaways = data['takeaways']

                if data.get('deadline'):
                    story.compliance_deadline = data['deadline']
                    story.deadline_description = data.get('deadline_description', '')

                if data.get('penalty_amount'):
                    story.penalty_amount = data['penalty_amount']

                if data.get('is_ai_related'):
                    story.is_ai_related = data['is_ai_related']
                else:
                    story.is_ai_related = False

            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract key parts
                story.enhanced_summary = story.summary
                story.is_ai_related = self._check_ai_related(story)

        except Exception as e:
            # On any error, keep original content
            print(f"  [ContentEnhancer] Error enhancing story: {e}")
            story.is_ai_related = self._check_ai_related(story)

        return story

    def _check_ai_related(self, story: NewsStory) -> bool:
        """Check if story is AI-related based on keywords."""
        text = f"{story.title} {story.summary}".lower()
        ai_keywords = [
            'artificial intelligence', 'ai ', ' ai,', 'machine learning', 'ml ',
            'neural network', 'deep learning', 'generative ai', 'chatgpt',
            'large language model', 'llm', 'foundation model', 'ai governance',
            'ai regulation', 'ai act', 'algorithmic', 'automated decision'
        ]
        return any(kw in text for kw in ai_keywords)

    def enhance_stories(self, stories: List[NewsStory],
                       verbose: bool = True) -> List[NewsStory]:
        """
        Enhance multiple stories.

        Args:
            stories: List of NewsStory objects
            verbose: Print progress

        Returns:
            List of enhanced stories
        """
        if not self.enabled:
            if verbose:
                print("  [ContentEnhancer] Disabled - using original content")
            # Still check AI-related status
            for story in stories:
                story.is_ai_related = self._check_ai_related(story)
            return stories

        enhanced = []
        for i, story in enumerate(stories):
            if verbose:
                print(f"  [ContentEnhancer] Enhancing story {i+1}/{len(stories)}: {story.title[:50]}...")

            enhanced_story = self.enhance_story(story)
            enhanced.append(enhanced_story)

        return enhanced


def extract_deadlines_from_stories(stories: List[NewsStory]) -> List[Dict]:
    """
    Extract all compliance deadlines from stories.

    Args:
        stories: List of NewsStory objects (enhanced)

    Returns:
        List of deadline dictionaries sorted by date
    """
    deadlines = []

    for story in stories:
        if hasattr(story, 'compliance_deadline') and story.compliance_deadline:
            try:
                deadline_date = datetime.strptime(story.compliance_deadline, '%Y-%m-%d')
                deadlines.append({
                    'date': deadline_date,
                    'date_str': story.compliance_deadline,
                    'description': getattr(story, 'deadline_description', story.title),
                    'jurisdiction': story.jurisdiction,
                    'story_title': story.title,
                    'url': story.url
                })
            except ValueError:
                continue

    # Sort by date
    deadlines.sort(key=lambda x: x['date'])

    return deadlines


def filter_ai_stories(stories: List[NewsStory]) -> List[NewsStory]:
    """
    Filter stories to only AI-related ones.

    Args:
        stories: List of NewsStory objects

    Returns:
        List of AI-related stories
    """
    return [s for s in stories if getattr(s, 'is_ai_related', False)]
