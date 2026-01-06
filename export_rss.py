#!/usr/bin/env python3
"""
Export legal digests to RSS feed format.

Usage:
    python export_rss.py [options]

Options:
    --output FILE       Output RSS file (default: output/feed.xml)
    --max-items N       Maximum items in feed (default: 20)
    --summary-only      Include only summary, not full content
    --feed-url URL      Base URL for the feed (default: https://example.com/digests)
    --validate          Validate the generated feed
"""
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from rss_exporter import RSSExporter


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Export legal digests to RSS feed',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--output',
        default='output/feed.xml',
        help='Output RSS file path (default: output/feed.xml)'
    )

    parser.add_argument(
        '--max-items',
        type=int,
        default=20,
        help='Maximum number of items in feed (default: 20)'
    )

    parser.add_argument(
        '--summary-only',
        action='store_true',
        help='Include only summary, not full content'
    )

    parser.add_argument(
        '--feed-url',
        default='https://example.com/digests',
        help='Base URL for the feed and digest links'
    )

    parser.add_argument(
        '--feed-title',
        default='Weekly APJ Legal Digest',
        help='Title of the RSS feed'
    )

    parser.add_argument(
        '--feed-description',
        default='Weekly digest of legal news covering Asia-Pacific jurisdictions, focused on technology law developments',
        help='Description of the RSS feed'
    )

    parser.add_argument(
        '--digest-dir',
        default='output',
        help='Directory containing digest markdown files (default: output)'
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate the generated RSS feed'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("RSS Feed Exporter")
    print("=" * 70)
    print()

    # Create exporter
    exporter = RSSExporter(
        feed_title=args.feed_title,
        feed_link=args.feed_url,
        feed_description=args.feed_description,
        base_url=args.feed_url
    )

    print(f"Feed configuration:")
    print(f"  Title: {args.feed_title}")
    print(f"  URL: {args.feed_url}")
    print(f"  Source: {args.digest_dir}")
    print(f"  Output: {args.output}")
    print(f"  Max items: {args.max_items}")
    print(f"  Content mode: {'Summary only' if args.summary_only else 'Full content'}")
    print()

    try:
        # Generate feed
        print("Generating RSS feed...")
        feed_path = exporter.generate_feed(
            digest_dir=args.digest_dir,
            output_file=args.output,
            max_items=args.max_items,
            include_full_content=not args.summary_only
        )

        print(f"✓ RSS feed generated: {feed_path}")
        print()

        # Get file size
        file_size = Path(feed_path).stat().st_size
        print(f"Feed size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
        print()

        # Validate if requested
        if args.validate:
            print("Validating RSS feed...")
            if exporter.validate_feed(feed_path):
                print("✓ Feed is valid")
            else:
                print("✗ Feed validation failed")
                return 1

        # Show usage instructions
        print()
        print("=" * 70)
        print("USAGE INSTRUCTIONS")
        print("=" * 70)
        print()
        print("1. Host the RSS feed:")
        print(f"   Upload '{args.output}' to your web server")
        print()
        print("2. Share the feed URL with subscribers:")
        print(f"   {args.feed_url}/feed.xml")
        print()
        print("3. Test the feed:")
        print("   - Open in an RSS reader (Feedly, Inoreader, etc.)")
        print("   - Validate at https://validator.w3.org/feed/")
        print()
        print("4. Update the feed:")
        print("   - Run this script again after generating new digests")
        print("   - The feed will automatically include the latest digests")
        print()

        return 0

    except Exception as e:
        print(f"✗ Error generating feed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
