"""Region insights generator for cross-jurisdictional patterns."""
from typing import List, Dict
from collections import Counter
from .news_collector import NewsStory
from .config import MAX_INSIGHTS_WORDS


class InsightsGenerator:
    """Generates regional insights from selected stories."""

    def __init__(self):
        self.max_words = MAX_INSIGHTS_WORDS

    def generate_insights(self, selected_stories: Dict[str, List[NewsStory]]) -> str:
        """
        Generate region insights section.

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

        # Analyze trends
        trends = self._identify_trends(all_stories)
        cross_border = self._identify_cross_border_impacts(all_stories)
        upcoming = self._identify_upcoming_items(all_stories)

        # Format insights
        insights = []

        if trends:
            insights.append(f"- **{trends['name']}:** {trends['description']}")

        if cross_border:
            insights.append(f"- **Cross-border impacts:** {cross_border}")

        if upcoming:
            insights.append(f"- **Upcoming:** {upcoming}")

        # Join and ensure word limit
        result = '\n'.join(insights)
        result = self._truncate_to_word_limit(result, self.max_words)

        return result

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
