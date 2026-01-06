"""Story selection logic with tier requirements."""
from typing import List, Dict
from .news_collector import NewsStory
from .config import (TIER1_JURISDICTIONS, TIER2_JURISDICTIONS,
                     TARGET_STORY_COUNT, TIER2_MAX_STORIES)


class StorySelector:
    """Selects stories based on tier requirements and limits."""

    def __init__(self, ranker):
        self.ranker = ranker

    def select_stories(self, stories: List[NewsStory]) -> Dict[str, List[NewsStory]]:
        """
        Select stories meeting all requirements.

        Args:
            stories: List of ranked NewsStory objects

        Returns:
            Dict mapping jurisdiction codes to selected stories
        """
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
