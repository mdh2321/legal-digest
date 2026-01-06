#!/usr/bin/env python3
"""
Run script for APAC Legal News Digest Generator.

This script is designed to be called from Claude Code which provides
the web search integration.
"""
import sys
import json
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


def main():
    """Main entry point."""
    # Check if results file provided
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
        print(f"Using cached results from: {results_file}")
        search_function = load_search_results(results_file)
    else:
        print("No search results provided, using mock search.")
        print("To use cached results: python run_digest.py <results.json>")
        search_function = create_mock_search_function()

    # Run generator
    generator = DigestGenerator(search_function=search_function)
    result = generator.run(verbose=True)

    if result is None:
        return 1

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Output file: {result['output_file']}")
    print(f"Total words: {result['stats']['word_count']}")
    print(f"Stories collected: {result['stats']['total_collected']}")
    print(f"Stories filtered: {result['stats']['filtered']}")
    print(f"Stories selected: {result['stats']['selected']}")
    print(f"Valid: {'Yes' if result['is_valid'] else 'No'}")
    print(f"Errors: {len(result['errors'])}")
    print(f"Warnings: {len(result['warnings'])}")
    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
