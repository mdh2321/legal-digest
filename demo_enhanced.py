#!/usr/bin/env python3
"""
Generate APJ Legal Digest with Enhanced Features

This script demonstrates the integrated enhanced digest generation system.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from generate_digest import DigestGenerator


def create_search_function():
    """Create a search function using Claude Code's web search."""
    def search_function(query):
        """
        This is a placeholder - in actual use, Claude Code provides the search function.
        For demonstration, we'll note that this would use Claude Code's WebSearch capability.
        """
        print(f"  Searching: {query}")
        # In actual use with Claude Code, this would return real search results
        return []

    return search_function


def main():
    print("=" * 70)
    print("APJ Legal Digest Generator - Enhanced Mode Demo")
    print("=" * 70)
    print()
    print("This script demonstrates the enhanced digest generation with:")
    print("  ✓ URL validation")
    print("  ✓ Content fetching")
    print("  ✓ Source credibility scoring")
    print("  ✓ LLM-powered summaries")
    print("  ✓ Professional formatting")
    print()

    # Create search function
    search_func = create_search_function()

    # Initialize generator with enhanced features enabled
    generator = DigestGenerator(
        search_function=search_func,
        use_enhanced_features=True  # Enable all enhancements
    )

    # Run digest generation
    result = generator.run(output_dir='output', verbose=True)

    if result:
        print()
        print("=" * 70)
        print("GENERATION COMPLETE")
        print("=" * 70)
        print(f"Output: {result['output_file']}")
        print(f"Word count: {result['stats']['word_count']}")
        print(f"Valid: {result['is_valid']}")

        if result['errors']:
            print(f"Errors: {len(result['errors'])}")
        if result['warnings']:
            print(f"Warnings: {len(result['warnings'])}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
