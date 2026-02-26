"""Markdown formatter for digest output."""
import re
from typing import List, Dict
from .news_collector import NewsStory
from .config import (ALL_JURISDICTIONS, TIER1_JURISDICTIONS,
                     TIER2_JURISDICTIONS, MAX_HEADLINE_WORDS)
from .date_utils import format_source_date, format_date_range
from .story_ranker import StoryRanker


class DigestFormatter:
    """Formats stories into markdown digest."""

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.split())

    def truncate_headline(self, headline: str) -> str:
        """
        Truncate headline to maximum word count.

        Args:
            headline: Original headline

        Returns:
            Truncated headline
        """
        words = headline.split()
        if len(words) <= MAX_HEADLINE_WORDS:
            return headline

        return ' '.join(words[:MAX_HEADLINE_WORDS]) + '...'

    def format_story(self, story: NewsStory) -> str:
        """
        Format a single story according to specification.

        Uses Claude-enhanced summary and takeaways when available.

        Args:
            story: NewsStory object

        Returns:
            Formatted markdown string
        """
        # Materiality label and source type
        materiality_label = StoryRanker.get_materiality_label(story)
        source_type = getattr(story, 'source_type', '')
        source_type_tag = f'`{source_type}`' if source_type else ''

        # Format headline with materiality label
        headline = self.truncate_headline(story.title)

        # Format source and date
        source_name = story.source if story.source else 'Source'
        source_date = format_source_date(story.date)
        source_link = f"[{source_name}]({story.url})"

        # Use enhanced summary if available
        enhanced_summary = getattr(story, 'enhanced_summary', None)
        summary = enhanced_summary or story.summary or story.snippet
        if not summary:
            summary = "Details available at source."

        # Clean up summary
        summary = summary.strip()
        if not summary.endswith('.'):
            summary += '.'

        # Use enhanced takeaways for "Why it matters" if available
        enhanced_takeaways = getattr(story, 'enhanced_takeaways', None)
        if enhanced_takeaways:
            relevance = enhanced_takeaways[0]
        else:
            relevance = self._generate_relevance(story)

        # Categories
        categories = ' '.join(f'`{cat}`' for cat in story.categories[:3])

        # Assemble story
        tags = f"{materiality_label} {source_type_tag} " if source_type_tag else f"{materiality_label} "
        story_text = f"- {tags}**{headline}** ({source_link}, {source_date})\n"
        story_text += f"  {summary}\n"
        story_text += f"  *Why it matters:* {relevance}\n"
        if categories:
            story_text += f"  {categories}\n"

        return story_text

    def _generate_relevance(self, story: NewsStory) -> str:
        """Generate 'why it matters' statement."""
        categories = story.categories

        if not categories:
            return "Affects regulatory compliance for technology operations."

        category_impacts = {
            'AI/ML': 'Impacts AI development and deployment strategies',
            'Data Privacy': 'Affects data handling and privacy compliance obligations',
            'Cybersecurity': 'Influences security requirements and breach response',
            'Cloud': 'Impacts cloud service agreements and vendor management',
            'eSignature': 'Affects digital transaction validity and authentication',
            'Contract Law': 'Shapes commercial contracting practices',
            'Competition': 'Impacts market strategy and merger activities',
            'Consumer Protection': 'Affects customer-facing practices and disclosures',
            'Corporate Governance': 'Influences board oversight and reporting duties',
            'Fintech': 'Impacts digital financial service offerings',
            'AML': 'Affects financial transaction monitoring obligations',
            'Anti-Bribery': 'Influences compliance programs and third-party due diligence',
            'Outsourcing': 'Impacts vendor contracts and service delivery models'
        }

        # Use first matching category
        for category in categories:
            if category in category_impacts:
                return category_impacts[category] + '.'

        return "Affects regulatory compliance for technology operations."

    def format_jurisdiction_section(self, jurisdiction: str,
                                      stories: List[NewsStory]) -> str:
        """
        Format a jurisdiction section.

        Args:
            jurisdiction: Two-letter jurisdiction code
            stories: List of NewsStory objects for this jurisdiction

        Returns:
            Formatted markdown section
        """
        if not stories:
            return ""

        jur_info = ALL_JURISDICTIONS[jurisdiction]
        flag = jur_info['flag']
        name = jur_info['name']

        section = f"## {flag}  {name}\n\n"

        for story in stories:
            section += self.format_story(story) + "\n"

        return section

    def format_digest(self, selected_stories: Dict[str, List[NewsStory]],
                      insights: str = "") -> str:
        """
        Format complete digest.

        Args:
            selected_stories: Dict mapping jurisdiction codes to stories
            insights: Region insights text

        Returns:
            Complete formatted markdown digest
        """
        # Calculate word count
        total_words = self._calculate_word_count(selected_stories, insights)

        # Header
        date_str = format_date_range(self.start_date, self.end_date)
        digest = f"# Weekly APJ Legal Digest — {date_str} (≈{total_words} words)\n\n"

        # Tier 1 jurisdictions
        for jur_code in TIER1_JURISDICTIONS.keys():
            if jur_code in selected_stories:
                section = self.format_jurisdiction_section(
                    jur_code, selected_stories[jur_code]
                )
                digest += section

        # Tier 2 jurisdictions (grouped)
        tier2_stories = {jur: stories for jur, stories in selected_stories.items()
                         if jur in TIER2_JURISDICTIONS}

        if tier2_stories:
            digest += "## 🌏  Other APJ\n\n"
            for jur_code, stories in tier2_stories.items():
                jur_name = ALL_JURISDICTIONS[jur_code]['name']
                digest += f"### {jur_name}\n\n"
                for story in stories:
                    digest += self.format_story(story) + "\n"

        # Region Insights
        if insights:
            digest += "## 📊  Region Insights\n\n"
            digest += insights + "\n"

        return digest

    def _calculate_word_count(self, selected_stories: Dict[str, List[NewsStory]],
                               insights: str) -> int:
        """Calculate total word count of digest."""
        total = 0

        # Count story words
        for stories in selected_stories.values():
            for story in stories:
                total += self.count_words(story.title)
                total += self.count_words(story.summary if story.summary else story.snippet)
                total += self.count_words(self._generate_relevance(story))

        # Count insights words
        if insights:
            total += self.count_words(insights)

        return total

    def expand_acronyms_in_story(self, story: NewsStory) -> NewsStory:
        """
        Expand acronyms in story text.

        Args:
            story: NewsStory object

        Returns:
            Story with expanded acronyms
        """
        from .content_filter import ContentFilter

        filter = ContentFilter(self.start_date, self.end_date)

        # Expand in title
        story.title = filter.expand_acronyms(story.title)

        # Expand in summary
        if story.summary:
            story.summary = filter.expand_acronyms(story.summary)

        return story
