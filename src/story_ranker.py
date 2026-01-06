"""Story ranking algorithm based on materiality and jurisdiction priority."""
from typing import List
from .news_collector import NewsStory
from .config import (ALL_JURISDICTIONS, MATERIALITY_WEIGHT,
                     JURISDICTION_WEIGHT, SOURCE_PRIORITY)


class StoryRanker:
    """Ranks stories based on materiality and jurisdiction priority."""

    def __init__(self):
        self.materiality_keywords = {
            'high': [
                'new regulation', 'new law', 'legislation passed',
                'court decision', 'supreme court', 'enforcement action',
                'regulatory guidance', 'policy change', 'compliance requirement',
                'fine', 'penalty', 'ruling', 'judgment', 'ban', 'prohibited'
            ],
            'medium': [
                'consultation', 'proposed regulation', 'draft law',
                'guidance', 'advisory', 'recommendation', 'update',
                'amendment', 'review', 'investigation'
            ],
            'low': [
                'discussion', 'opinion', 'analysis', 'commentary',
                'report', 'study', 'survey', 'trend'
            ]
        }

    def calculate_materiality_score(self, story: NewsStory) -> float:
        """
        Calculate materiality score based on content.

        Args:
            story: NewsStory object

        Returns:
            float: Materiality score (0.0 to 1.0)
        """
        text = f"{story.title} {story.summary}".lower()

        # Check for high materiality keywords
        high_count = sum(1 for kw in self.materiality_keywords['high']
                         if kw in text)
        medium_count = sum(1 for kw in self.materiality_keywords['medium']
                           if kw in text)
        low_count = sum(1 for kw in self.materiality_keywords['low']
                        if kw in text)

        # Calculate weighted score
        score = (high_count * 1.0 + medium_count * 0.6 + low_count * 0.3)

        # Normalize to 0-1 range (cap at 3 mentions)
        normalized = min(score / 3.0, 1.0)

        # Boost for regulatory sources
        if self._is_official_source(story.url):
            normalized = min(normalized * 1.3, 1.0)

        return normalized

    def _is_official_source(self, url: str) -> bool:
        """Check if URL is from an official government/regulatory source."""
        official_domains = [
            '.gov.', '.govt.', 'court', 'regulator',
            'legislation', 'parliament', 'congress'
        ]
        return any(domain in url.lower() for domain in official_domains)

    def get_jurisdiction_priority_score(self, jurisdiction: str) -> float:
        """
        Get priority score for jurisdiction.

        Args:
            jurisdiction: Two-letter jurisdiction code

        Returns:
            float: Priority score (0.0 to 1.0)
        """
        if jurisdiction not in ALL_JURISDICTIONS:
            return 0.0

        priority = ALL_JURISDICTIONS[jurisdiction]['priority']
        # Normalize: priority 4 (AU) = 1.0, priority 1 (others) = 0.25
        return priority / 4.0

    def calculate_overall_score(self, story: NewsStory) -> float:
        """
        Calculate overall ranking score.

        Args:
            story: NewsStory object

        Returns:
            float: Overall score
        """
        materiality = self.calculate_materiality_score(story)
        jurisdiction_priority = self.get_jurisdiction_priority_score(story.jurisdiction)

        # Apply weights
        overall = (materiality * MATERIALITY_WEIGHT +
                   jurisdiction_priority * JURISDICTION_WEIGHT)

        # Factor in relevance score from content filter
        if hasattr(story, 'relevance_score'):
            overall = overall * story.relevance_score

        story.materiality_score = materiality
        return overall

    def rank_stories(self, stories: List[NewsStory]) -> List[NewsStory]:
        """
        Rank stories by overall score.

        Args:
            stories: List of NewsStory objects

        Returns:
            List of stories sorted by score (highest first)
        """
        # Calculate scores
        for story in stories:
            story.overall_score = self.calculate_overall_score(story)

        # Sort by score descending
        ranked = sorted(stories, key=lambda s: s.overall_score, reverse=True)

        return ranked

    def get_top_stories_by_jurisdiction(self, stories: List[NewsStory],
                                         jurisdiction: str,
                                         count: int) -> List[NewsStory]:
        """
        Get top N stories for a specific jurisdiction.

        Args:
            stories: List of NewsStory objects
            jurisdiction: Two-letter jurisdiction code
            count: Number of stories to return

        Returns:
            List of top stories for jurisdiction
        """
        jur_stories = [s for s in stories if s.jurisdiction == jurisdiction]
        ranked = self.rank_stories(jur_stories)
        return ranked[:count]
