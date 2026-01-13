"""Story selection logic with tier requirements."""
import re
from typing import List, Dict, Set
from .news_collector import NewsStory
from .config import (TIER1_JURISDICTIONS, TIER2_JURISDICTIONS,
                     TARGET_STORY_COUNT, TIER2_MAX_STORIES, SOURCE_PRIORITY)


class StorySelector:
    """Selects stories based on tier requirements and limits."""

    def __init__(self, ranker):
        self.ranker = ranker

    def _get_source_priority(self, url: str) -> int:
        """
        Get source priority score based on URL domain.

        Priority hierarchy:
        - 3: Government/regulator sites (most authoritative)
        - 2: Major newspapers and legal publications
        - 1: Law firm publications

        Args:
            url: Story URL

        Returns:
            int: Priority score (higher = more authoritative)
        """
        url_lower = url.lower()

        # Government/regulator sites (highest priority)
        gov_patterns = ['.gov.', '.govt.', '.go.jp', '.go.kr', '.go.id']
        if any(pattern in url_lower for pattern in gov_patterns):
            return SOURCE_PRIORITY.get('government', 3)

        # Major legal publications and news outlets
        pub_patterns = [
            'lexology.com', 'law360.com', 'mondaq.com', 'iclg.com', 'iapp.org',
            'afr.com', 'straitstimes.com', 'nikkei.com', 'japantimes.co.jp',
            'koreaherald.com', 'scmp.com', 'barandbench.com', 'livelaw.in',
            'fpf.org', 'jdsupra.com'
        ]
        if any(pattern in url_lower for pattern in pub_patterns):
            return SOURCE_PRIORITY.get('legal_publication', 2)

        # Law firm sites (lowest priority - analysis/commentary)
        return SOURCE_PRIORITY.get('law_firm', 1)

    def _normalize_title(self, title: str) -> str:
        """
        Normalize title for comparison by removing common variations.

        Args:
            title: Original title

        Returns:
            Normalized title string
        """
        # Convert to lowercase
        normalized = title.lower()
        # Remove punctuation
        normalized = re.sub(r'[^\w\s]', '', normalized)
        # Remove common prefixes/suffixes
        prefixes_to_remove = [
            'breaking', 'update', 'alert', 'client alert', 'legal update',
            'news', 'analysis', 'commentary', 'insight', 'insights'
        ]
        for prefix in prefixes_to_remove:
            normalized = re.sub(rf'^{prefix}\s*:?\s*', '', normalized)
            normalized = re.sub(rf'\s*[–—-]\s*{prefix}$', '', normalized)
        # Normalize whitespace
        normalized = ' '.join(normalized.split())
        return normalized

    def _extract_key_terms(self, story: NewsStory) -> Set[str]:
        """
        Extract key terms from story for similarity comparison.

        Args:
            story: NewsStory object

        Returns:
            Set of key terms
        """
        text = f"{story.title} {story.summary}".lower()

        # Key entities to look for
        key_terms = set()

        # Extract regulator/organization names
        orgs = [
            'oaic', 'pdpc', 'ppc', 'mas', 'asic', 'accc', 'pipc', 'kcc',
            'meity', 'rbi', 'npc', 'imda', 'csa', 'meti', 'fsa'
        ]
        for org in orgs:
            if org in text:
                key_terms.add(org)

        # Extract action types
        actions = [
            'penalty', 'fine', 'enforcement', 'breach', 'consultation',
            'new law', 'act', 'regulation', 'guidance', 'framework'
        ]
        for action in actions:
            if action in text:
                key_terms.add(action)

        # Add jurisdiction
        key_terms.add(story.jurisdiction.lower())

        return key_terms

    def _are_stories_similar(self, story1: NewsStory, story2: NewsStory,
                             threshold: float = 0.6) -> bool:
        """
        Check if two stories are about the same news event.

        Uses title similarity and key term overlap.

        Args:
            story1: First story
            story2: Second story
            threshold: Similarity threshold (0-1)

        Returns:
            bool: True if stories appear to be duplicates
        """
        # Must be same jurisdiction
        if story1.jurisdiction != story2.jurisdiction:
            return False

        # Check normalized title similarity
        title1 = self._normalize_title(story1.title)
        title2 = self._normalize_title(story2.title)

        # Simple word overlap ratio
        words1 = set(title1.split())
        words2 = set(title2.split())

        if not words1 or not words2:
            return False

        intersection = words1 & words2
        union = words1 | words2
        title_similarity = len(intersection) / len(union)

        if title_similarity >= threshold:
            return True

        # Check key term overlap
        terms1 = self._extract_key_terms(story1)
        terms2 = self._extract_key_terms(story2)

        if terms1 and terms2:
            term_overlap = len(terms1 & terms2) / min(len(terms1), len(terms2))
            # High term overlap + moderate title similarity suggests same story
            if term_overlap >= 0.8 and title_similarity >= 0.4:
                return True

        return False

    def deduplicate_stories(self, stories: List[NewsStory]) -> List[NewsStory]:
        """
        Remove duplicate stories, keeping the highest-priority source.

        When multiple sources cover the same news event, keeps the most
        authoritative source based on priority hierarchy:
        1. Government/regulator announcements (priority 3)
        2. Legal publications/newspapers (priority 2)
        3. Law firm analysis (priority 1)

        Args:
            stories: List of stories (may contain duplicates)

        Returns:
            Deduplicated list with highest-priority sources retained
        """
        if not stories:
            return []

        # Sort by source priority (highest first), then by materiality score
        sorted_stories = sorted(
            stories,
            key=lambda s: (
                self._get_source_priority(s.url),
                getattr(s, 'materiality_score', 0)
            ),
            reverse=True
        )

        deduplicated = []
        for story in sorted_stories:
            # Check if this story is a duplicate of any already selected
            is_duplicate = False
            for selected in deduplicated:
                if self._are_stories_similar(story, selected):
                    is_duplicate = True
                    break

            if not is_duplicate:
                deduplicated.append(story)

        return deduplicated

    def select_stories(self, stories: List[NewsStory]) -> Dict[str, List[NewsStory]]:
        """
        Select stories meeting all requirements.

        Args:
            stories: List of ranked NewsStory objects

        Returns:
            Dict mapping jurisdiction codes to selected stories
        """
        # Step 0: Deduplicate stories (keeps highest-priority source for each event)
        stories = self.deduplicate_stories(stories)

        selected = {}

        # Step 1: Select minimum required stories from Tier 1
        for jur_code, jur_info in TIER1_JURISDICTIONS.items():
            min_stories = jur_info['min_stories']
            jur_stories = [s for s in stories if s.jurisdiction == jur_code]

            # Rank and take top N
            ranked = self.ranker.rank_stories(jur_stories)
            selected[jur_code] = ranked[:min_stories]

        # Step 2: Calculate remaining budget
        current_count = sum(len(stories) for stories in selected.values())
        min_target, max_target = TARGET_STORY_COUNT
        remaining_slots = max_target - current_count

        # Step 3: Select from Tier 1 (additional stories beyond minimum)
        tier1_pool = []
        for jur_code in TIER1_JURISDICTIONS.keys():
            jur_stories = [s for s in stories if s.jurisdiction == jur_code]
            selected_ids = {id(s) for s in selected.get(jur_code, [])}
            # Get stories not yet selected
            remaining = [s for s in jur_stories if id(s) not in selected_ids]
            tier1_pool.extend(remaining)

        # Rank and add best Tier 1 stories
        tier1_pool = self.ranker.rank_stories(tier1_pool)
        tier1_additions = min(len(tier1_pool), remaining_slots // 2)

        for story in tier1_pool[:tier1_additions]:
            if story.jurisdiction not in selected:
                selected[story.jurisdiction] = []
            selected[story.jurisdiction].append(story)
            remaining_slots -= 1

        # Step 4: Select from Tier 2 (max 3 total)
        tier2_pool = [s for s in stories
                      if s.jurisdiction in TIER2_JURISDICTIONS]
        tier2_pool = self.ranker.rank_stories(tier2_pool)

        tier2_count = 0
        tier2_selected = {}

        for story in tier2_pool:
            if tier2_count >= TIER2_MAX_STORIES:
                break
            if remaining_slots <= 0:
                break

            if story.jurisdiction not in tier2_selected:
                tier2_selected[story.jurisdiction] = []

            tier2_selected[story.jurisdiction].append(story)
            tier2_count += 1
            remaining_slots -= 1

        # Merge Tier 2 selections
        selected.update(tier2_selected)

        # Step 5: Ensure we meet minimum target if possible
        current_count = sum(len(stories) for stories in selected.values())
        if current_count < min_target:
            # Try to add more stories from any jurisdiction
            all_selected_ids = {id(s) for stories in selected.values() for s in stories}
            remaining_pool = [s for s in stories if id(s) not in all_selected_ids]
            remaining_pool = self.ranker.rank_stories(remaining_pool)

            needed = min_target - current_count
            for story in remaining_pool[:needed]:
                if story.jurisdiction not in selected:
                    selected[story.jurisdiction] = []
                selected[story.jurisdiction].append(story)

        return selected

    def get_story_count(self, selected: Dict[str, List[NewsStory]]) -> int:
        """
        Get total number of selected stories.

        Args:
            selected: Dict of selected stories

        Returns:
            Total count
        """
        return sum(len(stories) for stories in selected.values())

    def validate_selection(self, selected: Dict[str, List[NewsStory]]) -> bool:
        """
        Validate that selection meets requirements.

        Args:
            selected: Dict of selected stories

        Returns:
            bool: True if valid
        """
        # Check Tier 1 minimums
        for jur_code, jur_info in TIER1_JURISDICTIONS.items():
            if jur_code not in selected:
                return False
            if len(selected[jur_code]) < jur_info['min_stories']:
                return False

        # Check Tier 2 maximum
        tier2_count = sum(len(stories) for jur, stories in selected.items()
                          if jur in TIER2_JURISDICTIONS)
        if tier2_count > TIER2_MAX_STORIES:
            return False

        # Check total count
        total = self.get_story_count(selected)
        min_target, max_target = TARGET_STORY_COUNT
        # Allow going below minimum if there aren't enough quality stories
        if total > max_target:
            return False

        return True
