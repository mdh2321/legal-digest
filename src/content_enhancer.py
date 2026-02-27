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

        prompt = f"""You are a legal analyst writing for in-house counsel at a global SaaS company covering APJ.
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
    "summary": "A 3-4 sentence executive summary of what happened and why it matters for technology companies. Be specific about the regulation, law, or enforcement action. Include the who, what, when, and practical implications. Use plain language, no jargon or markdown formatting.",
    "takeaways": [
        "First specific, actionable takeaway for a SaaS company — BAD: 'Monitor developments'. GOOD: 'Review subscription agreements for compliance with new auto-renewal disclosure requirements under the amended Consumer Protection Act.'",
        "Second specific, actionable takeaway",
        "Third specific, actionable takeaway (if applicable)"
    ],
    "urgency": "immediate_action | monitor_closely | awareness_only",
    "urgency_reason": "One sentence explaining why this urgency level was assigned",
    "legal_area": "Primary legal area: Data Privacy, Cybersecurity, AI/ML, eSignature, Anti-Corruption, Consumer Protection, Competition, Employment, IP, Tax, Contract Law, Corporate Governance, Fintech, or other",
    "affects_contracts": true/false — does this require review of existing contracts or subscription terms?,
    "affects_product": true/false — does this affect product features, UX, or technical compliance?,
    "deadline": "YYYY-MM-DD format if a compliance deadline is mentioned, otherwise null",
    "deadline_description": "Brief description of what the deadline is for, or null",
    "penalty_amount": "Extracted fine/penalty amount with currency if mentioned, otherwise null",
    "is_ai_related": true/false based on whether this story involves AI/ML regulation
}}

GUIDELINES:
- Summary should explain WHAT happened, WHO is affected, and WHY it matters
- Takeaways must be specific and actionable — reference the actual law/regulation name, the specific compliance action required, and the affected business function
- urgency: use 'immediate_action' only for new obligations with near deadlines or enforcement actions; 'monitor_closely' for proposed laws, consultations, and developing enforcement trends; 'awareness_only' for analysis, guidance, and early-stage developments
- legal_area: pick the single most relevant area
- affects_contracts: true if the development could require changes to customer agreements, DPAs, vendor contracts, or terms of service
- affects_product: true if the development could require changes to product features, data flows, consent mechanisms, or user interfaces

Respond ONLY with the JSON object, no other text."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            print(f"  [ContentEnhancer] API response received for: {story.title[:50]}...")

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

                # New fields: urgency, legal_area, contract/product impact
                story.urgency = data.get('urgency', 'awareness_only')
                story.urgency_reason = data.get('urgency_reason', '')
                story.legal_area = data.get('legal_area', '')
                story.affects_contracts = data.get('affects_contracts', False)
                story.affects_product = data.get('affects_product', False)

                print(f"  [ContentEnhancer] SUCCESS enhanced: {story.title[:50]}...")

            except json.JSONDecodeError as je:
                # If JSON parsing fails, try to extract key parts
                print(f"  [ContentEnhancer] JSON parse failed for '{story.title[:50]}...': {je}")
                print(f"  [ContentEnhancer] Raw response: {response_text[:200]}...")
                story.enhanced_summary = story.summary
                story.is_ai_related = self._check_ai_related(story)

        except Exception as e:
            # On any error, keep original content
            print(f"  [ContentEnhancer] FAILED for '{story.title[:50]}...': {type(e).__name__}: {e}")
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


def generate_actions_summary(stories: List[NewsStory], client=None) -> Optional[str]:
    """
    Generate an "Actions This Week" summary from selected stories using Claude.

    Produces 4 subsections (~200 words total):
    1. Compliance deadlines
    2. Required reviews (affects_contracts == True)
    3. New obligations (urgency == 'immediate_action')
    4. Items to monitor (urgency == 'monitor_closely')

    Args:
        stories: List of enhanced NewsStory objects
        client: Optional anthropic.Anthropic client (creates one if not provided)

    Returns:
        Formatted actions summary text, or None if generation fails
    """
    if not stories:
        return None

    # Try to get a client
    if client is None:
        if not ANTHROPIC_AVAILABLE:
            return None
        api_key = load_api_key()
        if not api_key:
            return None
        try:
            client = anthropic.Anthropic(api_key=api_key)
        except Exception:
            return None

    # Build story context for the prompt
    story_details = []
    for s in stories:
        jur_name = ALL_JURISDICTIONS.get(s.jurisdiction, {}).get('name', s.jurisdiction)
        summary = getattr(s, 'enhanced_summary', None) or s.summary or s.snippet
        urgency = getattr(s, 'urgency', 'awareness_only')
        legal_area = getattr(s, 'legal_area', '')
        affects_contracts = getattr(s, 'affects_contracts', False)
        affects_product = getattr(s, 'affects_product', False)
        deadline = getattr(s, 'compliance_deadline', None)
        deadline_desc = getattr(s, 'deadline_description', '')

        detail = f"- [{jur_name}] {s.title} | urgency={urgency} | legal_area={legal_area}"
        detail += f" | affects_contracts={affects_contracts} | affects_product={affects_product}"
        if deadline:
            detail += f" | deadline={deadline} ({deadline_desc})"
        detail += f"\n  Summary: {summary[:200]}"
        story_details.append(detail)

    stories_text = '\n'.join(story_details)

    prompt = f"""You are writing an "Actions This Week" executive summary for in-house counsel at a global SaaS company covering APJ.

Based on these {len(stories)} stories, write a concise action summary (~200 words) with exactly 4 subsections:

1. **Compliance Deadlines** — list any specific dates or deadlines from the stories. If none, say "No new deadlines identified this week."
2. **Required Reviews** — list contracts, agreements, or terms that need review based on stories where affects_contracts=True. Be specific about which documents and why.
3. **New Obligations** — list any new compliance obligations from stories with urgency=immediate_action. Include the jurisdiction and specific requirement.
4. **Items to Monitor** — list developing regulatory trends from stories with urgency=monitor_closely. Note what to watch for and expected timeline.

Stories:
{stories_text}

Write in direct, actionable prose. No markdown formatting (no ** or *). Use plain text only. Use numbered sub-items within each section. Be specific — name the law, regulator, and jurisdiction."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.content[0].text.strip()
        print(f"  [ActionsGenerator] Generated actions summary ({len(result.split())} words)")
        return result
    except Exception as e:
        print(f"  [ActionsGenerator] Failed to generate actions summary: {e}")
        return None


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
