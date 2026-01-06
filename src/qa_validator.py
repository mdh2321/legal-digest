"""Quality assurance validation for digest output."""
from typing import List, Dict, Tuple
from .news_collector import NewsStory
from .config import (TIER1_JURISDICTIONS, TIER2_JURISDICTIONS,
                     TARGET_STORY_COUNT, TIER2_MAX_STORIES,
                     MAX_TOTAL_WORDS, MAX_INSIGHTS_WORDS)


class QAValidator:
    """Validates digest output against requirements."""

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.errors = []
        self.warnings = []

    def validate_all(self, selected_stories: Dict[str, List[NewsStory]],
                     digest_text: str) -> Tuple[bool, List[str], List[str]]:
        """
        Run all validation checks.

        Args:
            selected_stories: Dict mapping jurisdiction codes to stories
            digest_text: Final formatted digest text

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        # Run all checks
        self._check_date_range(selected_stories)
        self._check_jurisdictional_requirements(selected_stories)
        self._check_duplicates(selected_stories)
        self._check_word_count(digest_text)
        self._check_story_format(selected_stories, digest_text)
        self._check_urls(selected_stories)

        is_valid = len(self.errors) == 0

        return is_valid, self.errors, self.warnings

    def _check_date_range(self, selected_stories: Dict[str, List[NewsStory]]):
        """Check all stories are from correct week."""
        for jur, stories in selected_stories.items():
            for story in stories:
                story_date = story.date.date()
                if not (self.start_date <= story_date <= self.end_date):
                    self.errors.append(
                        f"Story '{story.title[:50]}' dated {story_date} is outside "
                        f"target week ({self.start_date} to {self.end_date})"
                    )

    def _check_jurisdictional_requirements(self,
                                            selected_stories: Dict[str, List[NewsStory]]):
        """Check minimum jurisdictional requirements met."""
        # Check Tier 1 minimums
        for jur_code, jur_info in TIER1_JURISDICTIONS.items():
            min_required = jur_info['min_stories']
            actual_count = len(selected_stories.get(jur_code, []))

            if actual_count < min_required:
                self.errors.append(
                    f"{jur_info['name']} requires minimum {min_required} "
                    f"story/stories, but only {actual_count} selected"
                )
            elif actual_count == 0:
                self.errors.append(
                    f"{jur_info['name']} has no stories selected (minimum: {min_required})"
                )

        # Check Tier 2 maximum
        tier2_count = sum(len(stories) for jur, stories in selected_stories.items()
                          if jur in TIER2_JURISDICTIONS)
        if tier2_count > TIER2_MAX_STORIES:
            self.warnings.append(
                f"Tier 2 jurisdictions have {tier2_count} stories "
                f"(maximum: {TIER2_MAX_STORIES})"
            )

        # Check total count
        total_count = sum(len(stories) for stories in selected_stories.values())
        min_target, max_target = TARGET_STORY_COUNT

        if total_count < min_target:
            self.warnings.append(
                f"Total story count ({total_count}) is below target minimum ({min_target})"
            )
        elif total_count > max_target:
            self.errors.append(
                f"Total story count ({total_count}) exceeds maximum ({max_target})"
            )

    def _check_duplicates(self, selected_stories: Dict[str, List[NewsStory]]):
        """Check for duplicate stories."""
        seen_urls = set()
        seen_titles = set()

        for stories in selected_stories.values():
            for story in stories:
                # Check URL duplicates
                if story.url in seen_urls:
                    self.errors.append(f"Duplicate URL found: {story.url}")
                seen_urls.add(story.url)

                # Check title duplicates (warning only)
                title_lower = story.title.lower()
                if title_lower in seen_titles:
                    self.warnings.append(f"Similar title found: {story.title[:50]}")
                seen_titles.add(title_lower)

    def _check_word_count(self, digest_text: str):
        """Check total word count."""
        word_count = len(digest_text.split())

        if word_count > MAX_TOTAL_WORDS:
            self.warnings.append(
                f"Total word count ({word_count}) exceeds target ({MAX_TOTAL_WORDS})"
            )

    def _check_story_format(self, selected_stories: Dict[str, List[NewsStory]],
                            digest_text: str):
        """Check story formatting requirements."""
        for stories in selected_stories.values():
            for story in stories:
                # Check headline exists
                if not story.title or len(story.title.strip()) == 0:
                    self.errors.append("Story missing headline")

                # Check URL exists
                if not story.url or len(story.url.strip()) == 0:
                    self.errors.append(f"Story '{story.title[:50]}' missing URL")

                # Check categories assigned
                if not story.categories or len(story.categories) == 0:
                    self.warnings.append(
                        f"Story '{story.title[:50]}' has no category tags"
                    )

                # Check summary exists
                if not story.summary and not story.snippet:
                    self.warnings.append(
                        f"Story '{story.title[:50]}' missing summary"
                    )

    def _check_urls(self, selected_stories: Dict[str, List[NewsStory]]):
        """Check URL formatting."""
        for stories in selected_stories.values():
            for story in stories:
                url = story.url

                # Check for URL shorteners
                shorteners = ['bit.ly', 't.co', 'tinyurl', 'goo.gl']
                if any(shortener in url for shortener in shorteners):
                    self.warnings.append(
                        f"URL shortener detected in {url} (prefer permalinks)"
                    )

                # Check for tracking parameters (should be cleaned)
                tracking_params = ['utm_', 'fbclid', 'gclid']
                if any(param in url for param in tracking_params):
                    self.warnings.append(
                        f"Tracking parameters detected in {url}"
                    )

    def get_validation_report(self) -> str:
        """Generate validation report."""
        report = []

        if not self.errors and not self.warnings:
            return "✓ All quality assurance checks passed"

        if self.errors:
            report.append("ERRORS:")
            for error in self.errors:
                report.append(f"  ✗ {error}")

        if self.warnings:
            report.append("\nWARNINGS:")
            for warning in self.warnings:
                report.append(f"  ⚠ {warning}")

        return '\n'.join(report)
