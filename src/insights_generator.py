"""Region insights generator for cross-jurisdictional patterns."""
import os
from typing import List, Dict, Optional
from collections import Counter
from .news_collector import NewsStory
from .config import MAX_INSIGHTS_WORDS, ALL_JURISDICTIONS

# Try to import anthropic for Claude-powered insights
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class InsightsGenerator:
    """Generates regional insights from selected stories."""

    def __init__(self):
        self.max_words = MAX_INSIGHTS_WORDS

    def generate_insights(self, selected_stories: Dict[str, List[NewsStory]]) -> str:
        """
        Generate region insights section.

        When Claude API is available, generates a brief Editor's Note
        summarizing the most consequential developments and cross-jurisdictional
        patterns. Falls back to category-counting logic otherwise.

        Args:
            selected_stories: Dict mapping jurisdiction codes to stories

        Returns:
            Formatted insights text (≤120 words)
        """
        # Flatten stories
        all_stories = []
        for stories in selected_stories.values():
            all_stories.extend(stories)

        if not all_stories:
            return ""

        # Try Claude-powered insights first
        claude_insights = self._generate_claude_insights(all_stories)
        if claude_insights:
            return claude_insights

        # Fall back to rule-based insights
        trends = self._identify_trends(all_stories)
        cross_border = self._identify_cross_border_impacts(all_stories)
        upcoming = self._identify_upcoming_items(all_stories)

        insights = []

        if trends:
            insights.append(f"{trends['name']}: {trends['description']}")

        if cross_border:
            insights.append(f"Cross-border impacts: {cross_border}")

        if upcoming:
            insights.append(f"Upcoming: {upcoming}")

        result = '\n'.join(insights)
        result = self._truncate_to_word_limit(result, self.max_words)

        return result

    def _generate_claude_insights(self, stories: List[NewsStory]) -> Optional[str]:
        """Generate an Editor's Note using Claude API."""
        if not ANTHROPIC_AVAILABLE:
            return None

        api_key = self._load_api_key()
        if not api_key:
            return None

        # Build story summaries for the prompt (include urgency and legal_area)
        story_summaries = []
        for s in stories[:12]:
            jur_name = ALL_JURISDICTIONS.get(s.jurisdiction, {}).get('name', s.jurisdiction)
            summary = getattr(s, 'enhanced_summary', None) or s.summary or s.snippet
            cats = ', '.join(s.categories[:3]) if s.categories else 'General'
            urgency = getattr(s, 'urgency', 'awareness_only')
            legal_area = getattr(s, 'legal_area', cats)
            story_summaries.append(
                f"- [{jur_name}] {s.title}: {summary} "
                f"(Legal area: {legal_area}, Urgency: {urgency})"
            )

        stories_text = '\n'.join(story_summaries)

        prompt = f"""You are the editor of a weekly APAC legal digest for in-house counsel at global SaaS companies.

Based on these {len(stories)} stories from this week's digest, write an "Editor's Note" (150-200 words) covering:

1. CROSS-JURISDICTIONAL TRENDS: Name specific countries and their actions that show emerging patterns (e.g., "Australia, Singapore, and Japan all advanced AI governance frameworks this week...").
2. CONVERGENCE/DIVERGENCE: Where are regulators aligning versus diverging? What does this mean for a company operating across multiple APJ markets?
3. WHAT TO WATCH NEXT WEEK: Mention specific open consultations, upcoming effective dates, or expected regulatory announcements.

Stories:
{stories_text}

Write in a direct, analytical tone. Use flowing prose, not bullet points. Do NOT use markdown formatting (no ** or *). Use plain text only. Be specific — name countries, laws, and regulators. Start with "Editor's Note:" """

        try:
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.content[0].text.strip()
            return self._truncate_to_word_limit(result, self.max_words)
        except Exception as e:
            print(f"  [InsightsGenerator] Claude API failed, using fallback: {e}")
            return None

    @staticmethod
    def _load_api_key() -> Optional[str]:
        """Load API key from environment or file."""
        key = os.environ.get('ANTHROPIC_API_KEY')
        if key:
            return key
        from pathlib import Path
        key_file = Path(__file__).parent.parent / 'api_key.txt'
        if key_file.exists():
            k = key_file.read_text().strip()
            if k and not k.startswith('#'):
                return k
        return None

    def _identify_trends(self, stories: List[NewsStory]) -> Dict[str, str]:
        """Identify dominant trends across stories."""
        # Count categories
        category_counts = Counter()
        for story in stories:
            for category in story.categories:
                category_counts[category] += 1

        if not category_counts:
            return {}

        # Most common category
        top_category, count = category_counts.most_common(1)[0]

        if count < 2:
            return {}

        # Generate trend description
        trend_descriptions = {
            'AI/ML': 'Multiple jurisdictions advancing AI governance frameworks',
            'Data Privacy': 'Regional harmonization of data protection standards continues',
            'Cybersecurity': 'Enhanced cybersecurity mandates emerging across region',
            'Cloud': 'Cloud sovereignty and data residency requirements tightening',
            'Fintech': 'Digital finance regulation maturing across APJ markets',
            'Competition': 'Heightened antitrust scrutiny of tech platforms',
            'Consumer Protection': 'Stronger consumer safeguards for digital services',
            'Corporate Governance': 'ESG and transparency requirements expanding'
        }

        description = trend_descriptions.get(
            top_category,
            'Regulatory activity increasing across technology sector'
        )

        return {
            'name': f'{top_category} Focus',
            'description': description
        }

    def _identify_cross_border_impacts(self, stories: List[NewsStory]) -> str:
        """Identify cross-border implications."""
        # Check for stories affecting multiple jurisdictions
        jurisdictions = set(story.jurisdiction for story in stories)

        if len(jurisdictions) < 2:
            return ""

        # Check for common themes
        category_counts = Counter()
        for story in stories:
            for category in category_counts:
                category_counts[category] += 1

        # Look for categories appearing in multiple jurisdictions
        multi_jurisdiction_categories = []
        for category in set(cat for story in stories for cat in story.categories):
            jurs_with_category = set()
            for story in stories:
                if category in story.categories:
                    jurs_with_category.add(story.jurisdiction)
            if len(jurs_with_category) >= 2:
                multi_jurisdiction_categories.append(category)

        if multi_jurisdiction_categories:
            category = multi_jurisdiction_categories[0]
            return f"{category} developments affecting multinational operations and compliance strategies."

        return "Diverse regulatory developments requiring jurisdiction-specific compliance approaches."

    def _identify_upcoming_items(self, stories: List[NewsStory]) -> str:
        """Identify upcoming deadlines and consultations."""
        # Look for keywords indicating future events
        future_keywords = [
            'consultation', 'deadline', 'upcoming', 'proposed',
            'draft', 'comment period', 'effective date', 'coming into force'
        ]

        upcoming_stories = []
        for story in stories:
            text = f"{story.title} {story.summary}".lower()
            if any(keyword in text for keyword in future_keywords):
                upcoming_stories.append(story)

        if not upcoming_stories:
            return "Monitor ongoing regulatory consultations and guidance updates."

        # Summarize
        if len(upcoming_stories) == 1:
            return "Key consultation period or deadline mentioned in featured developments."
        else:
            return f"Multiple consultation periods and implementation deadlines across {len(upcoming_stories)} jurisdictions."

    def _truncate_to_word_limit(self, text: str, max_words: int) -> str:
        """Truncate text to word limit."""
        words = text.split()
        if len(words) <= max_words:
            return text

        # Truncate and add ellipsis
        truncated = ' '.join(words[:max_words])

        # Try to end at a sentence
        if '.' in truncated:
            last_period = truncated.rfind('.')
            truncated = truncated[:last_period + 1]

        return truncated
