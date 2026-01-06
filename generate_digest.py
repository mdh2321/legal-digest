#!/usr/bin/env python3
"""
APAC Legal News Digest Generator - Enhanced Version

Generates a weekly digest of legal news covering Asia-Pacific jurisdictions,
focused on technology law developments relevant to global tech companies.

Enhanced features:
- URL validation and content fetching
- Source credibility scoring
- LLM-powered summaries and analysis
- Professional formatting
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


class DigestGenerator:
    """Main orchestrator for digest generation with enhanced features."""

    def __init__(self, search_function=None, use_enhanced_features=True):
        """
        Initialize generator.

        Args:
            search_function: Function that takes a query and returns search results
                            If None, will need to be provided when running
            use_enhanced_features: Enable URL validation, content fetching, and LLM summaries
        """
        self.search_function = search_function
        self.start_date = None
        self.end_date = None
        self.use_enhanced_features = use_enhanced_features

    def run(self, output_dir: str = 'output', verbose: bool = True):
        """
        Run the complete digest generation process.

        Args:
            output_dir: Directory to save output
            verbose: Print progress messages
        """
        if verbose:
            print("=" * 70)
            print("APAC Legal News Digest Generator")
            if self.use_enhanced_features:
                print("Enhanced Mode: URL validation + content fetching + LLM summaries")
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
            if self.use_enhanced_features:
                print("  Enhanced features: URL validation + content fetching enabled")

        collector = NewsCollector(
            self.start_date,
            self.end_date,
            enable_validation=self.use_enhanced_features,
            enable_content_fetch=self.use_enhanced_features
        )

        if self.search_function is None:
            print("  ERROR: No search function provided.")
            print("  This script requires integration with a web search capability.")
            print("  Please run via the integrated workflow or provide search_function.")
            return None

        all_stories = collector.collect_all_stories(self.search_function)

        if verbose:
            print(f"  Collected {len(all_stories)} stories")
            if self.use_enhanced_features:
                validated_count = sum(1 for s in all_stories if s.is_url_validated)
                with_content = sum(1 for s in all_stories if s.article_content)
                avg_credibility = sum(s.credibility_score for s in all_stories) / len(all_stories) if all_stories else 0
                print(f"    URLs validated: {validated_count}")
                print(f"    Full content fetched: {with_content}")
                print(f"    Avg source credibility: {avg_credibility:.2f}")

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
            if self.use_enhanced_features:
                print(f"  Ranked {len(ranked_stories)} stories by materiality, jurisdiction, and source credibility")
            else:
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

        # Step 6: Generate insights and enhanced content
        if verbose:
            print("\n[6/8] Generating insights and enhanced summaries...")

        # Generate LLM-powered summaries if enhanced features enabled
        executive_summary = ""
        cross_jurisdictional_analysis = ""

        if self.use_enhanced_features:
            try:
                from src.llm_summarizer import LLMSummarizer

                llm = LLMSummarizer(use_claude=True)

                if verbose:
                    print("  Generating LLM-powered story summaries...")

                # Generate enhanced summaries for each story
                story_count = 0
                for jur, stories in selected_stories.items():
                    for i, story in enumerate(stories):
                        story_count += 1
                        # Use article content if available, otherwise snippet
                        content = story.article_content if story.article_content else story.snippet

                        # Generate comprehensive summary
                        summary = llm.generate_story_summary(
                            content, story.title, max_words=150
                        )
                        story.summary = summary

                        # Generate contextual "why it matters"
                        why_it_matters = llm.generate_why_it_matters(
                            content, story.title, story.categories, jur
                        )
                        story.why_it_matters = why_it_matters

                        selected_stories[jur][i] = story

                if verbose:
                    print(f"    Enhanced {story_count} story summaries")
                    print("  Generating executive summary...")

                # Generate executive summary
                executive_summary = llm.generate_executive_summary(
                    selected_stories, max_words=200
                )

                if verbose:
                    print("  Generating cross-jurisdictional analysis...")

                # Generate cross-jurisdictional analysis
                cross_jurisdictional_analysis = llm.generate_cross_jurisdictional_analysis(
                    selected_stories, max_words=400
                )

            except ImportError as e:
                if verbose:
                    print(f"  Note: LLM features not available ({e}), using standard summaries")
            except Exception as e:
                if verbose:
                    print(f"  Note: LLM generation failed ({e}), using standard summaries")

        # Generate standard insights (backward compatibility)
        insights_gen = InsightsGenerator()
        insights = insights_gen.generate_insights(selected_stories)

        if verbose:
            if executive_summary:
                print(f"  Executive summary: {len(executive_summary.split())} words")
            if cross_jurisdictional_analysis:
                print(f"  Cross-jurisdictional analysis: {len(cross_jurisdictional_analysis.split())} words")
            else:
                word_count = len(insights.split())
                print(f"  Generated insights ({word_count} words)")

        # Step 7: Format digest
        if verbose:
            print("\n[7/8] Formatting digest...")

        # Use enhanced formatter if available and features enabled
        if self.use_enhanced_features:
            try:
                from src.formatter_enhanced import EnhancedDigestFormatter

                formatter = EnhancedDigestFormatter(self.start_date, self.end_date)

                # Expand acronyms in stories
                for jur, stories in selected_stories.items():
                    for i, story in enumerate(stories):
                        selected_stories[jur][i] = formatter.expand_acronyms_in_story(story)

                digest_text = formatter.format_digest(
                    selected_stories,
                    insights=insights,
                    executive_summary=executive_summary,
                    cross_jurisdictional_analysis=cross_jurisdictional_analysis
                )

                if verbose:
                    total_words = len(digest_text.split())
                    read_time = formatter.estimate_read_time(total_words)
                    print(f"  Enhanced digest: {total_words} words (~{read_time} min read)")

            except ImportError as e:
                if verbose:
                    print(f"  Note: Enhanced formatter not available ({e}), using standard formatter")
                # Fall back to standard formatter
                formatter = DigestFormatter(self.start_date, self.end_date)

                for jur, stories in selected_stories.items():
                    for i, story in enumerate(stories):
                        selected_stories[jur][i] = formatter.expand_acronyms_in_story(story)

                digest_text = formatter.format_digest(selected_stories, insights)

                if verbose:
                    total_words = len(digest_text.split())
                    print(f"  Formatted digest ({total_words} words)")
        else:
            # Use standard formatter
            formatter = DigestFormatter(self.start_date, self.end_date)

            for jur, stories in selected_stories.items():
                for i, story in enumerate(stories):
                    selected_stories[jur][i] = formatter.expand_acronyms_in_story(story)

            digest_text = formatter.format_digest(selected_stories, insights)

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

        filename = f"digest_{self.end_date.strftime('%Y-%m-%d')}.md"
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
