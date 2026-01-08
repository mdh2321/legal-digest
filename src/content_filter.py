"""Content filtering based on inclusion/exclusion rules."""
import re
from typing import List
from .news_collector import NewsStory
from .config import EXCLUDE_TOPICS, INCLUDE_TOPICS


class ContentFilter:
    """Filters news stories based on content rules."""

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def should_exclude(self, story: NewsStory) -> bool:
        """
        Check if story should be excluded based on topic.

        Args:
            story: NewsStory object

        Returns:
            bool: True if story should be excluded
        """
        text = f"{story.title} {story.summary}".lower()

        for exclude_keyword in EXCLUDE_TOPICS:
            if exclude_keyword.lower() in text:
                return True

        return False

    def is_in_date_range(self, story: NewsStory) -> bool:
        """
        Check if story date is within target week (STRICT enforcement).

        This is a critical filter - only articles published within the
        exact target week (Monday-Sunday) should pass.

        Args:
            story: NewsStory object

        Returns:
            bool: True if date is strictly within the target week range
        """
        story_date = story.date.date()

        # Strict check: must be >= start_date AND <= end_date
        in_range = self.start_date <= story_date <= self.end_date

        # Log rejection for debugging
        if not in_range:
            print(f"  [DATE FILTER] Rejected: '{story.title[:50]}...' "
                  f"(date: {story_date}, range: {self.start_date} to {self.end_date})")

        return in_range

    def get_matching_categories(self, story: NewsStory) -> List[str]:
        """
        Get categories that match the story content.

        Args:
            story: NewsStory object

        Returns:
            List of matching category names
        """
        text = f"{story.title} {story.summary}".lower()
        matching = []

        for category, keywords in INCLUDE_TOPICS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    matching.append(category)
                    break  # Only add category once

        return matching

    def calculate_relevance_score(self, story: NewsStory) -> float:
        """
        Calculate how relevant the story is to tech law topics.

        Args:
            story: NewsStory object

        Returns:
            float: Relevance score (0.0 to 1.0)
        """
        categories = self.get_matching_categories(story)
        story.categories = categories

        if not categories:
            return 0.0

        # Base score from number of matching categories
        base_score = min(len(categories) / 3.0, 1.0)

        # Boost for high-priority topics
        priority_topics = {'AI/ML', 'Data Privacy', 'Cybersecurity', 'Fintech'}
        has_priority = any(cat in priority_topics for cat in categories)

        if has_priority:
            base_score = min(base_score * 1.2, 1.0)

        return base_score

    def filter_stories(self, stories: List[NewsStory]) -> List[NewsStory]:
        """
        Filter stories based on all criteria.

        Args:
            stories: List of NewsStory objects

        Returns:
            List of filtered NewsStory objects
        """
        filtered = []

        for story in stories:
            # Check exclusions
            if self.should_exclude(story):
                continue

            # Check date range
            if not self.is_in_date_range(story):
                continue

            # Calculate relevance
            relevance = self.calculate_relevance_score(story)
            if relevance < 0.3:  # Minimum relevance threshold
                continue

            story.relevance_score = relevance
            filtered.append(story)

        return filtered

    def expand_acronyms(self, text: str) -> str:
        """
        Expand common acronyms on first use.

        Args:
            text: Text to process

        Returns:
            Text with acronyms expanded
        """
        acronym_map = {
            'AI': 'Artificial Intelligence (AI)',
            'ML': 'Machine Learning (ML)',
            'GDPR': 'General Data Protection Regulation (GDPR)',
            'PDPA': 'Personal Data Protection Act (PDPA)',
            'PDPC': 'Personal Data Protection Commission (PDPC)',
            'AML': 'Anti-Money Laundering (AML)',
            'KYC': 'Know Your Customer (KYC)',
            'API': 'Application Programming Interface (API)',
            'SaaS': 'Software as a Service (SaaS)',
            'PaaS': 'Platform as a Service (PaaS)',
            'IaaS': 'Infrastructure as a Service (IaaS)',
            'ESG': 'Environmental, Social, and Governance (ESG)',
            'ACCC': 'Australian Competition and Consumer Commission (ACCC)',
            'MAS': 'Monetary Authority of Singapore (MAS)',
            'ASIC': 'Australian Securities and Investments Commission (ASIC)'
        }

        result = text
        expanded = set()

        # Find acronyms in text
        for acronym, expansion in acronym_map.items():
            # Only expand first occurrence
            if acronym in text and acronym not in expanded:
                # Use word boundary to match whole words
                pattern = r'\b' + re.escape(acronym) + r'\b'
                result = re.sub(pattern, expansion, result, count=1)
                expanded.add(acronym)

        return result
