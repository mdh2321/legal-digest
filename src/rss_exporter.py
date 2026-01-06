"""RSS feed exporter for legal digests."""
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from email.utils import formatdate
import xml.etree.ElementTree as ET
from xml.dom import minidom


class RSSExporter:
    """Exports digests to RSS 2.0 format."""

    def __init__(self, feed_title: str = "Weekly APJ Legal Digest",
                 feed_link: str = "https://example.com/digests",
                 feed_description: str = "Weekly digest of legal news covering Asia-Pacific jurisdictions",
                 base_url: str = "https://example.com/digests"):
        """
        Initialize RSS exporter.

        Args:
            feed_title: Title of the RSS feed
            feed_link: URL where the feed is published
            feed_description: Description of the feed
            base_url: Base URL for individual digest links
        """
        self.feed_title = feed_title
        self.feed_link = feed_link
        self.feed_description = feed_description
        self.base_url = base_url

    def parse_digest_file(self, digest_path: str) -> Optional[Dict]:
        """
        Parse a digest markdown file to extract metadata and content.

        Args:
            digest_path: Path to digest markdown file

        Returns:
            Dict with digest metadata and content, or None if parsing fails
        """
        try:
            with open(digest_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract title and date from header
            title_match = re.search(r'^# (.+?)(?:\s+\(≈\d+\s+words\))?$', content, re.MULTILINE)
            if not title_match:
                return None

            title = title_match.group(1).strip()

            # Extract date from filename (digest_YYYY-MM-DD.md)
            filename = os.path.basename(digest_path)
            date_match = re.search(r'digest_(\d{4}-\d{2}-\d{2})', filename)
            if not date_match:
                return None

            date_str = date_match.group(1)
            pub_date = datetime.strptime(date_str, '%Y-%m-%d')

            # Generate summary from first few stories
            summary = self._generate_summary(content)

            return {
                'title': title,
                'pub_date': pub_date,
                'date_str': date_str,
                'content': content,
                'summary': summary,
                'filename': filename
            }
        except Exception as e:
            print(f"Error parsing {digest_path}: {e}")
            return None

    def _generate_summary(self, content: str) -> str:
        """
        Generate a summary from digest content.

        Args:
            content: Full digest markdown content

        Returns:
            Summary text
        """
        # Extract jurisdiction sections
        sections = re.findall(r'##\s+🇦🇺\s+Australia|##\s+🇸🇬\s+Singapore|##\s+🇯🇵\s+Japan', content)
        jurisdictions = []

        if '🇦🇺' in content or 'Australia' in content:
            jurisdictions.append('Australia')
        if '🇸🇬' in content or 'Singapore' in content:
            jurisdictions.append('Singapore')
        if '🇯🇵' in content or 'Japan' in content:
            jurisdictions.append('Japan')

        # Count stories
        story_count = len(re.findall(r'^- \*\*', content, re.MULTILINE))

        if jurisdictions:
            jur_list = ', '.join(jurisdictions[:3])
            if len(jurisdictions) > 3:
                jur_list += f' and {len(jurisdictions) - 3} more'
            return f"This week's digest covers {story_count} legal technology developments from {jur_list}."
        else:
            return f"This week's digest covers {story_count} legal technology developments across APAC."

    def _convert_markdown_to_html(self, content: str) -> str:
        """
        Convert markdown digest to HTML for RSS.

        Args:
            content: Markdown content

        Returns:
            HTML content
        """
        # Simple markdown to HTML conversion
        html = content

        # Convert headers
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)

        # Convert bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        # Convert italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # Convert links
        html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)

        # Convert code blocks
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

        # Convert list items
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

        # Wrap consecutive list items in <ul>
        html = re.sub(r'(<li>.+?</li>(?:\n<li>.+?</li>)*)', r'<ul>\1</ul>', html, flags=re.DOTALL)

        # Convert paragraphs (text between blank lines)
        paragraphs = html.split('\n\n')
        formatted_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith('<'):
                para = f'<p>{para}</p>'
            formatted_paragraphs.append(para)

        html = '\n'.join(formatted_paragraphs)

        return html

    def generate_feed(self, digest_dir: str = 'output',
                      output_file: str = 'feed.xml',
                      max_items: int = 20,
                      include_full_content: bool = True) -> str:
        """
        Generate RSS feed from digest files.

        Args:
            digest_dir: Directory containing digest markdown files
            output_file: Output RSS feed file path
            max_items: Maximum number of items to include in feed
            include_full_content: If True, include full digest; if False, summary only

        Returns:
            Path to generated RSS feed file
        """
        # Find all digest files
        digest_path = Path(digest_dir)
        digest_files = sorted(digest_path.glob('digest_*.md'), reverse=True)

        if not digest_files:
            raise ValueError(f"No digest files found in {digest_dir}")

        # Parse digest files
        digests = []
        for digest_file in digest_files[:max_items]:
            digest_data = self.parse_digest_file(str(digest_file))
            if digest_data:
                digests.append(digest_data)

        # Create RSS feed
        rss = ET.Element('rss', version='2.0')
        rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')

        channel = ET.SubElement(rss, 'channel')

        # Channel metadata
        ET.SubElement(channel, 'title').text = self.feed_title
        ET.SubElement(channel, 'link').text = self.feed_link
        ET.SubElement(channel, 'description').text = self.feed_description

        # Self-referencing link
        atom_link = ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link')
        atom_link.set('href', f"{self.feed_link}/{output_file}")
        atom_link.set('rel', 'self')
        atom_link.set('type', 'application/rss+xml')

        # Language and other metadata
        ET.SubElement(channel, 'language').text = 'en-us'
        ET.SubElement(channel, 'lastBuildDate').text = formatdate(timeval=datetime.now().timestamp(), localtime=False, usegmt=True)

        # Add items
        for digest in digests:
            item = ET.SubElement(channel, 'item')

            ET.SubElement(item, 'title').text = digest['title']

            # Link to digest
            link = f"{self.base_url}/{digest['date_str']}"
            ET.SubElement(item, 'link').text = link

            # Description (summary or full content)
            if include_full_content:
                description = self._convert_markdown_to_html(digest['content'])
            else:
                description = digest['summary']

            ET.SubElement(item, 'description').text = f"<![CDATA[{description}]]>"

            # Publication date
            pub_date_str = formatdate(timeval=digest['pub_date'].timestamp(), localtime=False, usegmt=True)
            ET.SubElement(item, 'pubDate').text = pub_date_str

            # GUID (unique identifier)
            guid = ET.SubElement(item, 'guid')
            guid.text = f"digest-{digest['date_str']}"
            guid.set('isPermaLink', 'false')

        # Convert to string with proper formatting
        xml_str = ET.tostring(rss, encoding='unicode')

        # Pretty print
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent='  ', encoding='utf-8')

        # Write to file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(pretty_xml)

        return str(output_path)

    def validate_feed(self, feed_path: str) -> bool:
        """
        Validate RSS feed structure.

        Args:
            feed_path: Path to RSS feed file

        Returns:
            True if valid, False otherwise
        """
        try:
            tree = ET.parse(feed_path)
            root = tree.getroot()

            # Check RSS structure
            if root.tag != 'rss':
                print("Error: Root element is not 'rss'")
                return False

            channel = root.find('channel')
            if channel is None:
                print("Error: No 'channel' element found")
                return False

            # Check required channel elements
            required = ['title', 'link', 'description']
            for elem in required:
                if channel.find(elem) is None:
                    print(f"Error: Required element '{elem}' not found in channel")
                    return False

            # Check items
            items = channel.findall('item')
            if not items:
                print("Warning: No items in feed")

            for i, item in enumerate(items):
                if item.find('title') is None:
                    print(f"Error: Item {i} missing title")
                    return False

            print(f"✓ Feed validation passed ({len(items)} items)")
            return True

        except Exception as e:
            print(f"Error validating feed: {e}")
            return False
