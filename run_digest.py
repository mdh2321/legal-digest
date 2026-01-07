#!/usr/bin/env python3
"""
Run script for APAC Legal News Digest Generator.

This script is designed to be called from Claude Code which provides
the web search integration.
"""
import sys
import json
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from generate_digest import DigestGenerator


def create_mock_search_function():
    """
    Create a mock search function for testing.

    In production, this is replaced by actual web search integration.
    """
    def mock_search(query):
        """Mock search function that returns empty results."""
        print(f"  Mock search: {query}")
        return []

    return mock_search


def load_search_results(results_file: str):
    """
    Load pre-fetched search results from a JSON file.

    Args:
        results_file: Path to JSON file with search results

    Returns:
        Function that returns cached results
    """
    with open(results_file, 'r') as f:
        cached_results = json.load(f)

    def cached_search(query):
        """Return cached results for query."""
        return cached_results.get(query, [])

    return cached_search


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='APAC Legal News Digest Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_digest.py --format rss
  python run_digest.py --format markdown --output ./digests
  python run_digest.py --format rss --results search_results.json
  python run_digest.py --publish  # Output to docs/ for GitHub Pages
        """
    )

    parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'rss'],
        default='rss',
        help='Output format: markdown or rss (default: rss)'
    )

    parser.add_argument(
        '--output', '-o',
        default='output',
        help='Output directory (default: output)'
    )

    parser.add_argument(
        '--publish', '-p',
        action='store_true',
        help='Publish to docs/ for GitHub Pages (also creates feed.xml)'
    )

    parser.add_argument(
        '--results', '-r',
        help='JSON file with cached search results (optional)'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress output'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Set up search function
    if args.results:
        print(f"Using cached results from: {args.results}")
        search_function = load_search_results(args.results)
    else:
        print("No search results provided, using mock search.")
        print("To use cached results: python run_digest.py --results <results.json>")
        search_function = create_mock_search_function()

    # Determine output directory
    if args.publish:
        output_dir = Path(__file__).parent / 'docs'
        output_format = 'rss'  # Always RSS for publishing
    else:
        output_dir = args.output
        output_format = args.format

    # Run generator
    generator = DigestGenerator(search_function=search_function)
    result = generator.run(
        output_dir=str(output_dir),
        output_format=output_format,
        verbose=not args.quiet
    )

    if result is None:
        return 1

    # If publishing, also create feed.xml for stable URL
    if args.publish and result.get('output_file'):
        import shutil
        output_file = Path(result['output_file'])
        feed_file = output_file.parent / 'feed.xml'
        shutil.copy(output_file, feed_file)
        if not args.quiet:
            print(f"Published to: {feed_file}")
            print(f"RSS URL: https://mdh2321.github.io/legal-digest/feed.xml")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Output format: {output_format.upper()}")
    print(f"Output file: {result['output_file']}")
    if output_format == 'markdown':
        print(f"Total words: {result['stats']['word_count']}")
    print(f"Stories collected: {result['stats']['total_collected']}")
    print(f"Stories filtered: {result['stats']['filtered']}")
    print(f"Stories selected: {result['stats']['selected']}")
    print(f"Valid: {'Yes' if result['is_valid'] else 'No'}")
    print(f"Errors: {len(result['errors'])}")
    print(f"Warnings: {len(result['warnings'])}")
    if args.publish:
        print("-" * 70)
        print("GitHub Pages URL: https://mdh2321.github.io/legal-digest/feed.xml")
    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
