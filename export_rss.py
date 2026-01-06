#!/usr/bin/env python3
"""
RSS Feed Exporter for APAC Legal News Digests

Converts markdown digests to RSS 2.0 format for feed readers.
"""
import sys
import re
from pathlib import Path
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from xml.dom import minidom


class DigestParser:
    """Parses markdown digest files."""

    def __init__(self, digest_path: Path):
        self.path = digest_path
        self.content = digest_path.read_text(encoding='utf-8')

    def extract_metadata(self):
        """Extract digest metadata from markdown."""
        # Extract title and date from header
        # Format: # Weekly APJ Legal Digest — DD Month YYYY (≈XXX words)
        title_match = re.search(r'^# (.+?) \(≈\d+ words\)', self.content, re.MULTILINE)
        if not title_match:
            return None

        title = title_match.group(1).strip()

        # Extract date from filename (digest_YYYY-MM-DD.md)
        date_match = re.search(r'digest_(\d{4}-\d{2}-\d{2})\.md', self.path.name)
        if date_match:
            pub_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
        else:
            pub_date = datetime.fromtimestamp(self.path.stat().st_mtime)

        return {
            'title': title,
            'pub_date': pub_date,
            'filename': self.path.name
        }

    def extract_stories(self):
        """Extract individual stories from digest."""
        stories = []

        # Split by jurisdiction sections (## with flag emoji)
        sections = re.split(r'\n## (?:🇦🇺|🇸🇬|🇯🇵|🌏)', self.content)

        for section in sections[1:]:  # Skip the title section
            # Extract stories from this section (- **[Headline]** format)
            story_pattern = r'- \*\*(.+?)\*\* \(\[(.+?)\]\((.+?)\), (.+?)\)\s+(.+?)\s+\*Why it matters:\* (.+?)(?:\s+`.*?`)*\n'
            matches = re.finditer(story_pattern, section, re.DOTALL)

            for match in matches:
                headline = match.group(1).strip()
                source = match.group(2).strip()
                url = match.group(3).strip()
                date_str = match.group(4).strip()
                summary = match.group(5).strip()
                relevance = match.group(6).strip()

                # Clean up summary
                summary = ' '.join(summary.split())
                relevance = ' '.join(relevance.split())

                stories.append({
                    'title': headline,
                    'url': url,
                    'source': source,
                    'date': date_str,
                    'summary': summary,
                    'relevance': relevance
                })

        return stories


class RSSExporter:
    """Exports digests to RSS 2.0 format."""

    def __init__(self, channel_title="APAC Legal News Digest",
                 channel_link="https://mdh2321.github.io/legal-digest",
                 channel_description="Weekly digest of legal news covering Asia-Pacific jurisdictions, focused on technology law developments."):
        self.channel_title = channel_title
        self.channel_link = channel_link
        self.channel_description = channel_description

    def create_feed(self, digests_data):
        """
        Create RSS feed from digest data.

        Args:
            digests_data: List of tuples (metadata, stories) for each digest

        Returns:
            XML string of RSS feed
        """
        # Create root RSS element
        rss = Element('rss', version='2.0')
        rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')

        # Create channel
        channel = SubElement(rss, 'channel')

        # Channel metadata
        SubElement(channel, 'title').text = self.channel_title
        SubElement(channel, 'link').text = self.channel_link
        SubElement(channel, 'description').text = self.channel_description
        SubElement(channel, 'language').text = 'en'
        SubElement(channel, 'lastBuildDate').text = self._format_rfc822(datetime.now())

        # Add items for each digest
        for metadata, stories in digests_data:
            self._add_digest_item(channel, metadata, stories)

        return self._prettify_xml(rss)

    def _add_digest_item(self, channel, metadata, stories):
        """Add a digest as an RSS item."""
        item = SubElement(channel, 'item')

        # Item metadata
        SubElement(item, 'title').text = metadata['title']
        SubElement(item, 'link').text = f"{self.channel_link}/{metadata['filename']}"
        SubElement(item, 'pubDate').text = self._format_rfc822(metadata['pub_date'])
        SubElement(item, 'guid', isPermaLink='false').text = f"digest-{metadata['pub_date'].strftime('%Y-%m-%d')}"

        # Create description with story summaries
        description = self._create_html_description(stories)
        SubElement(item, 'description').text = description

    def _create_html_description(self, stories):
        """Create HTML description of stories for RSS."""
        html_parts = ['<div>']

        for i, story in enumerate(stories[:10], 1):  # Limit to first 10 stories
            html_parts.append(f'<p><strong>{i}. {story["title"]}</strong></p>')
            html_parts.append(f'<p>{story["summary"]}</p>')
            html_parts.append(f'<p><em>Why it matters:</em> {story["relevance"]}</p>')
            html_parts.append(f'<p><a href="{story["url"]}">{story["source"]}</a> • {story["date"]}</p>')

            if i < len(stories[:10]):
                html_parts.append('<hr/>')

        html_parts.append('</div>')
        return ''.join(html_parts)

    def _format_rfc822(self, dt):
        """Format datetime as RFC 822 for RSS."""
        return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')

    def _prettify_xml(self, elem):
        """Return a pretty-printed XML string."""
        rough_string = tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')


def main():
    """Main entry point."""
    print("=" * 70)
    print("APAC Legal News Digest - RSS Exporter")
    print("=" * 70)

    # Find all digest files
    output_dir = Path('output')
    digest_files = sorted(output_dir.glob('digest_*.md'), reverse=True)

    if not digest_files:
        print("\nNo digest files found in output directory.")
        print("Please generate digests first using generate_digest.py")
        return 1

    print(f"\nFound {len(digest_files)} digest file(s)")

    # Parse all digests
    digests_data = []
    for digest_file in digest_files:
        print(f"  Processing: {digest_file.name}")

        parser = DigestParser(digest_file)
        metadata = parser.extract_metadata()

        if not metadata:
            print(f"    ⚠ Could not parse metadata, skipping")
            continue

        stories = parser.extract_stories()
        print(f"    Found {len(stories)} stories")

        digests_data.append((metadata, stories))

    if not digests_data:
        print("\nNo valid digests to export.")
        return 1

    # Create RSS feed
    print(f"\nGenerating RSS feed...")
    exporter = RSSExporter()
    rss_xml = exporter.create_feed(digests_data)

    # Save RSS feed
    output_file = output_dir / 'digest_feed.xml'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(rss_xml)

    print(f"✓ RSS feed saved to: {output_file}")
    print(f"  Channel: {exporter.channel_title}")
    print(f"  Items: {len(digests_data)}")

    # Show sample
    print("\n" + "=" * 70)
    print("Sample RSS output:")
    print("=" * 70)
    print(rss_xml[:1000] + "...")

    print("\n" + "=" * 70)
    print("Export complete!")
    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
