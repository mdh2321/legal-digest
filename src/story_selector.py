"""Story selection logic with tier requirements."""
import re
from typing import List, Dict, Set
from .news_collector import NewsStory
from .config import (TIER1_JURISDICTIONS, TIER2_JURISDICTIONS,
                     EXTRATERRITORIAL_JURISDICTIONS,
                     MIN_STORIES, DEFAULT_MAX_STORIES, BUSY_WEEK_MAX_STORIES,
                     TIER1_MAX_PER_JURISDICTION, TIER2_MAX_STORIES,
                     EXTRA_MAX_STORIES, MATERIALITY_EXPANSION_THRESHOLD,
                     SOURCE_PRIORITY)


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

    def _extract_proper_nouns(self, text: str) -> Set[str]:
        """Extract likely proper nouns / entity names from text."""
        # Match capitalized multi-word names (e.g. "FIIG Securities", "OAIC")
        entities = set()
        for match in re.finditer(r'\b[A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)*\b', text):
            word = match.group()
            # Skip common title-case words
            if word.lower() not in {'the', 'a', 'an', 'and', 'or', 'for', 'in', 'on', 'to',
                                     'new', 'law', 'court', 'act', 'bill', 'draft'}:
                entities.add(word.lower())
        return entities

    def _are_stories_similar(self, story1: NewsStory, story2: NewsStory,
                             threshold: float = 0.4) -> bool:
        """
        Check if two stories are about the same news event.

        Uses exact URL match (cross-jurisdiction), then title similarity,
        key term overlap, and entity matching (same jurisdiction only).

        Args:
            story1: First story
            story2: Second story
            threshold: Similarity threshold (0-1)

        Returns:
            bool: True if stories appear to be duplicates
        """
        # Exact URL match = always duplicate regardless of jurisdiction
        if story1.url == story2.url:
            return True

        # For content-based similarity, must be same jurisdiction
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
            # High term overlap + any title similarity suggests same story
            if term_overlap >= 0.8 and title_similarity >= 0.3:
                return True

        # Check entity overlap (catches same story from different outlets)
        entities1 = self._extract_proper_nouns(story1.title)
        entities2 = self._extract_proper_nouns(story2.title)
        shared_entities = entities1 & entities2
        if len(shared_entities) >= 2 and title_similarity >= 0.25:
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
        Select stories using demand-driven dynamic volume.

        Logic:
        1. Tier 1 minimums (1 each AU, SG, JP)
        2. Tier 1 expansion: additional stories above threshold, up to TIER1_MAX_PER_JURISDICTION
        3. Tier 2 selection: stories above threshold, up to TIER2_MAX_STORIES total
        4. Extraterritorial: up to EXTRA_MAX_STORIES from 'EXTRA'
        5. Floor: if below MIN_STORIES, backfill from best remaining
        6. Ceiling: if above BUSY_WEEK_MAX_STORIES, trim lowest-scoring (preserving Tier 1 minimums)

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
            ranked = self.ranker.rank_stories(jur_stories)
            selected[jur_code] = ranked[:min_stories]

        # Step 2: Tier 1 expansion — add stories above threshold up to per-jurisdiction cap
        for jur_code in TIER1_JURISDICTIONS.keys():
            jur_stories = [s for s in stories if s.jurisdiction == jur_code]
            ranked = self.ranker.rank_stories(jur_stories)
            selected_ids = {id(s) for s in selected.get(jur_code, [])}
            current_count = len(selected.get(jur_code, []))

            for story in ranked:
                if current_count >= TIER1_MAX_PER_JURISDICTION:
                    break
                if id(story) in selected_ids:
                    continue
                if getattr(story, 'overall_score', 0) >= MATERIALITY_EXPANSION_THRESHOLD:
                    selected[jur_code].append(story)
                    selected_ids.add(id(story))
                    current_count += 1

        # Step 3: Tier 2 selection — stories above threshold up to TIER2_MAX_STORIES total
        tier2_pool = [s for s in stories if s.jurisdiction in TIER2_JURISDICTIONS]
        tier2_pool = self.ranker.rank_stories(tier2_pool)

        tier2_count = 0
        for story in tier2_pool:
            if tier2_count >= TIER2_MAX_STORIES:
                break
            if getattr(story, 'overall_score', 0) >= MATERIALITY_EXPANSION_THRESHOLD:
                if story.jurisdiction not in selected:
                    selected[story.jurisdiction] = []
                selected[story.jurisdiction].append(story)
                tier2_count += 1

        # Step 4: Extraterritorial — up to EXTRA_MAX_STORIES
        extra_pool = [s for s in stories if s.jurisdiction == 'EXTRA']
        extra_pool = self.ranker.rank_stories(extra_pool)
        extra_selected = extra_pool[:EXTRA_MAX_STORIES]
        if extra_selected:
            selected['EXTRA'] = extra_selected

        # Step 5: Floor — backfill if below MIN_STORIES
        current_total = sum(len(st) for st in selected.values())
        if current_total < MIN_STORIES:
            all_selected_ids = {id(s) for st in selected.values() for s in st}
            remaining_pool = [s for s in stories if id(s) not in all_selected_ids]
            remaining_pool = self.ranker.rank_stories(remaining_pool)

            needed = MIN_STORIES - current_total
            for story in remaining_pool[:needed]:
                if story.jurisdiction not in selected:
                    selected[story.jurisdiction] = []
                selected[story.jurisdiction].append(story)

        # Step 6: Ceiling — trim if above BUSY_WEEK_MAX_STORIES
        current_total = sum(len(st) for st in selected.values())
        if current_total > BUSY_WEEK_MAX_STORIES:
            # Collect all selected with scores, preserving Tier 1 minimums
            all_selected = []
            for jur, st_list in selected.items():
                for s in st_list:
                    all_selected.append((jur, s))

            # Sort by score ascending (lowest first = candidates for removal)
            all_selected.sort(key=lambda x: getattr(x[1], 'overall_score', 0))

            # Track Tier 1 counts to protect minimums
            tier1_counts = {jur: len(st) for jur, st in selected.items()
                           if jur in TIER1_JURISDICTIONS}

            to_remove = current_total - BUSY_WEEK_MAX_STORIES
            removed = set()
            for jur, story in all_selected:
                if to_remove <= 0:
                    break
                # Protect Tier 1 minimums
                if jur in TIER1_JURISDICTIONS:
                    min_req = TIER1_JURISDICTIONS[jur]['min_stories']
                    if tier1_counts.get(jur, 0) <= min_req:
                        continue
                    tier1_counts[jur] -= 1
                removed.add(id(story))
                to_remove -= 1

            # Rebuild selected without removed stories
            for jur in list(selected.keys()):
                selected[jur] = [s for s in selected[jur] if id(s) not in removed]
                if not selected[jur]:
                    del selected[jur]

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

        # Check total count — ceiling is a soft limit (warning, not failure)
        total = self.get_story_count(selected)
        if total > BUSY_WEEK_MAX_STORIES:
            return False

        return True
