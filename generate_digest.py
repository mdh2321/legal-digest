#!/usr/bin/env python3
"""
APAC Legal News Digest Generator

Generates a weekly digest of legal news covering Asia-Pacific jurisdictions,
focused on technology law developments relevant to global tech companies.
"""
import sys
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.date_utils import get_last_week_range, get_week_description
from src.news_collector import NewsCollector
from src.content_filter import ContentFilter
from src.story_ranker import StoryRanker
from src.story_selector import StorySelector
from src.formatter import DigestFormatter
from src.insights_generator import InsightsGenerator
from src.qa_validator import QAValidator
from src.rss_generator import RSSGenerator


class DigestGenerator:
    """Main orchestrator for digest generation."""

    def __init__(self, search_function=None):
        """
        Initialize generator.

        Args:
            search_function: Function that takes a query and returns search results
                            If None, will need to be provided when running
        """
        self.search_function = search_function
        self.start_date = None
        self.end_date = None

    def run(self, output_dir: str = 'output', output_format: str = 'markdown',
            verbose: bool = True):
        """
        Run the complete digest generation process.

        Args:
            output_dir: Directory to save output
            output_format: Output format - 'markdown' or 'rss'
            verbose: Print progress messages
        """
        if verbose:
            print("=" * 70)
            print("APAC Legal News Digest Generator")
            print("=" * 70)

        # Step 1: Calculate date range
        if verbose:
            print("\n[1/8] Calculating date range...")

        self.start_date, self.end_date = get_last_week_range()
        week_desc = get_week_description(self.start_date, self.end_date)

        if verbose:
            print(f"  Target week: {week_desc}")

        # Step 2: Collect news stories
        if verbose:
            print("\n[2/8] Collecting news stories...")

        collector = NewsCollector(self.start_date, self.end_date)

        if self.search_function is None:
            print("  ERROR: No search function provided.")
            print("  This script requires integration with a web search capability.")
            print("  Please run via the integrated workflow or provide search_function.")
            return None

        all_stories = collector.collect_all_stories(self.search_function)

        if verbose:
            print(f"  Collected {len(all_stories)} stories")

        # Step 3: Filter stories
        if verbose:
            print("\n[3/8] Filtering stories...")

        content_filter = ContentFilter(self.start_date, self.end_date)
        filtered_stories = content_filter.filter_stories(all_stories)

        if verbose:
            print(f"  {len(filtered_stories)} stories passed filters")

        # Step 4: Rank stories
        if verbose:
            print("\n[4/8] Ranking stories...")

        ranker = StoryRanker()
        ranked_stories = ranker.rank_stories(filtered_stories)

        if verbose:
            print(f"  Ranked {len(ranked_stories)} stories by materiality and jurisdiction")

        # Step 5: Select stories
        if verbose:
            print("\n[5/8] Selecting stories...")

        selector = StorySelector(ranker)
        selected_stories = selector.select_stories(ranked_stories)

        total_selected = selector.get_story_count(selected_stories)
        if verbose:
            print(f"  Selected {total_selected} stories")
            for jur, stories in selected_stories.items():
                from src.config import ALL_JURISDICTIONS
                jur_name = ALL_JURISDICTIONS[jur]['name']
                print(f"    {jur_name}: {len(stories)}")

        # Step 6: Generate insights
        if verbose:
            print("\n[6/8] Generating region insights...")

        insights_gen = InsightsGenerator()
        insights = insights_gen.generate_insights(selected_stories)

        if verbose:
            word_count = len(insights.split())
            print(f"  Generated insights ({word_count} words)")

        # Step 7: Format digest
        if verbose:
            print(f"\n[7/8] Formatting digest ({output_format})...")

        formatter = DigestFormatter(self.start_date, self.end_date)

        # Expand acronyms in stories
        for jur, stories in selected_stories.items():
            for i, story in enumerate(stories):
                selected_stories[jur][i] = formatter.expand_acronyms_in_story(story)

        if output_format == 'rss':
            rss_gen = RSSGenerator(self.start_date, self.end_date)
            digest_text = rss_gen.generate_feed(selected_stories, insights)
            file_extension = 'xml'
            if verbose:
                print(f"  Generated RSS feed")
        else:
            digest_text = formatter.format_digest(selected_stories, insights)
            file_extension = 'md'
            if verbose:
                total_words = len(digest_text.split())
                print(f"  Formatted digest ({total_words} words)")

        # Step 8: Validate
        if verbose:
            print("\n[8/8] Running quality assurance...")

        validator = QAValidator(self.start_date, self.end_date)
        is_valid, errors, warnings = validator.validate_all(selected_stories, digest_text)

        if verbose:
            if is_valid:
                print("  ✓ All validation checks passed")
            else:
                print(f"  ✗ {len(errors)} errors found")

            if warnings:
                print(f"  ⚠ {len(warnings)} warnings")

            # Print validation report
            report = validator.get_validation_report()
            if report:
                print("\n" + report)

        # Save output
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        filename = f"digest_{self.end_date.strftime('%Y-%m-%d')}.{file_extension}"
        output_file = output_path / filename

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(digest_text)

        if verbose:
            print(f"\n✓ Digest saved to: {output_file}")
            print("=" * 70)

        return {
            'digest_text': digest_text,
            'output_file': str(output_file),
            'is_valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'stats': {
                'total_collected': len(all_stories),
                'filtered': len(filtered_stories),
                'selected': total_selected,
                'word_count': len(digest_text.split())
            }
        }


def main():
    """Main entry point."""
    print("APAC Legal News Digest Generator")
    print()
    print("This script requires integration with a web search service.")
    print("Please use the integrated workflow or provide a search function.")
    print()
    print("For manual usage, see README.md for instructions.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
