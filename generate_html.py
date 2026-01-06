#!/usr/bin/env python3
"""
Generate HTML Pages from Markdown Digests

Converts markdown digest files to styled HTML pages for web viewing.
"""
import sys
import re
import json
from pathlib import Path
from datetime import datetime


class MarkdownToHTMLConverter:
    """Converts digest markdown to HTML."""

    def __init__(self):
        self.html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
            line-height: 1.6;
            color: #333;
            background: #f9f9f9;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: #3498db;
            text-decoration: none;
            font-weight: 500;
        }}
        .back-link:hover {{
            text-decoration: underline;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 2em;
        }}
        h2 {{
            color: #2c3e50;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
            font-size: 1.6em;
        }}
        h3 {{
            color: #34495e;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        .story {{
            margin: 25px 0;
            padding: 20px;
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }}
        .story-headline {{
            font-size: 1.2em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
        }}
        .story-meta {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 12px;
        }}
        .story-meta a {{
            color: #3498db;
            text-decoration: none;
        }}
        .story-meta a:hover {{
            text-decoration: underline;
        }}
        .story-summary {{
            color: #555;
            line-height: 1.7;
            margin-bottom: 12px;
        }}
        .story-relevance {{
            color: #555;
            font-style: italic;
            margin-bottom: 12px;
        }}
        .story-relevance strong {{
            color: #2c3e50;
            font-style: normal;
        }}
        .story-tags {{
            margin-top: 12px;
        }}
        .tag {{
            display: inline-block;
            background: #ecf0f1;
            color: #2c3e50;
            padding: 4px 10px;
            border-radius: 3px;
            font-size: 0.85em;
            margin-right: 6px;
            margin-top: 4px;
            font-family: 'Courier New', monospace;
        }}
        .insights {{
            background: #e8f4f8;
            padding: 25px;
            border-radius: 4px;
            margin-top: 30px;
            border-left: 4px solid #3498db;
        }}
        .insights h2 {{
            margin-top: 0;
            border-bottom: none;
        }}
        .insights ul {{
            margin: 15px 0;
            padding-left: 20px;
        }}
        .insights li {{
            margin: 12px 0;
            line-height: 1.7;
        }}
        .insights strong {{
            color: #2c3e50;
        }}
        footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #777;
            font-size: 0.9em;
        }}
        footer a {{
            color: #3498db;
            text-decoration: none;
        }}
        footer a:hover {{
            text-decoration: underline;
        }}
        @media (max-width: 768px) {{
            body {{
                margin: 20px auto;
            }}
            .container {{
                padding: 20px;
            }}
            h1 {{
                font-size: 1.5em;
            }}
            h2 {{
                font-size: 1.3em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="index.html" class="back-link">← Back to All Digests</a>
        {content}
        <footer>
            <p>Generated using the <a href="https://github.com/mdh2321/legal-digest">APAC Legal News Digest Generator</a></p>
        </footer>
    </div>
</body>
</html>"""

    def parse_markdown(self, md_content):
        """Parse markdown content into structured data."""
        lines = md_content.split('\n')
        html_parts = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Main heading (h1)
            if line.startswith('# '):
                title = line[2:].strip()
                html_parts.append(f'<h1>{self.escape_html(title)}</h1>')

            # Section heading (h2)
            elif line.startswith('## '):
                section = line[3:].strip()
                if '📊  Region Insights' in section:
                    # Start insights section
                    html_parts.append('<div class="insights">')
                    html_parts.append(f'<h2>{self.escape_html(section)}</h2>')
                else:
                    html_parts.append(f'<h2>{self.escape_html(section)}</h2>')

            # Subsection (h3)
            elif line.startswith('### '):
                subsection = line[4:].strip()
                html_parts.append(f'<h3>{self.escape_html(subsection)}</h3>')

            # Story item
            elif line.startswith('- **'):
                story_html = self.parse_story(lines, i)
                html_parts.append(story_html)

            # List items (for insights)
            elif line.startswith('- '):
                # Check if we're in insights section
                if any('insights' in str(p).lower() for p in html_parts[-3:]):
                    if '<ul>' not in ''.join(html_parts[-5:]):
                        html_parts.append('<ul>')
                    item_text = line[2:].strip()
                    html_parts.append(f'<li>{self.parse_inline_markdown(item_text)}</li>')

                    # Check if next line is not a list item, close ul
                    if i + 1 >= len(lines) or not lines[i + 1].startswith('- '):
                        html_parts.append('</ul>')

            i += 1

        # Close insights div if it was opened
        if '<div class="insights">' in ''.join(html_parts):
            html_parts.append('</div>')

        return ''.join(html_parts)

    def parse_story(self, lines, start_idx):
        """Parse a story block into HTML."""
        story_parts = []
        story_parts.append('<div class="story">')

        # First line: headline and meta
        line = lines[start_idx]
        headline_match = re.match(r'- \*\*(.+?)\*\* \(\[(.+?)\]\((.+?)\), (.+?)\)', line)

        if headline_match:
            headline = headline_match.group(1)
            source = headline_match.group(2)
            url = headline_match.group(3)
            date = headline_match.group(4)

            story_parts.append(f'<div class="story-headline">{self.escape_html(headline)}</div>')
            story_parts.append(f'<div class="story-meta"><a href="{self.escape_html(url)}" target="_blank">{self.escape_html(source)}</a> • {self.escape_html(date)}</div>')

        # Following lines: summary, relevance, tags
        i = start_idx + 1
        while i < len(lines):
            line = lines[i].strip()

            if not line or line.startswith('- **') or line.startswith('## ') or line.startswith('### '):
                break

            # Summary (indented, not italic)
            if line.startswith('  ') and not line.startswith('  *'):
                summary = line.strip()
                story_parts.append(f'<div class="story-summary">{self.escape_html(summary)}</div>')

            # Relevance (Why it matters)
            elif '*Why it matters:*' in line:
                relevance = line.replace('*Why it matters:*', '').strip()
                story_parts.append(f'<div class="story-relevance"><strong>Why it matters:</strong> {self.escape_html(relevance)}</div>')

            # Tags
            elif '`' in line:
                tags = re.findall(r'`([^`]+)`', line)
                if tags:
                    story_parts.append('<div class="story-tags">')
                    for tag in tags:
                        story_parts.append(f'<span class="tag">{self.escape_html(tag)}</span>')
                    story_parts.append('</div>')

            i += 1

        story_parts.append('</div>')
        return ''.join(story_parts)

    def parse_inline_markdown(self, text):
        """Parse inline markdown (bold, links, etc.)."""
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

        # Links
        text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', text)

        return self.escape_html_preserve_tags(text)

    def escape_html(self, text):
        """Escape HTML special characters."""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))

    def escape_html_preserve_tags(self, text):
        """Escape HTML but preserve already converted tags."""
        # This is a simplified version - assumes parse_inline_markdown was called
        return text

    def convert(self, md_content, title):
        """Convert markdown to full HTML page."""
        html_content = self.parse_markdown(md_content)
        return self.html_template.format(
            title=self.escape_html(title),
            content=html_content
        )


def update_index_with_digests(digest_list, index_path):
    """Update index.html with digest list."""
    index_html = index_path.read_text(encoding='utf-8')

    # Create JavaScript array for digests
    digests_js = json.dumps(digest_list, indent=12)

    # Replace the digests array in the JavaScript
    # Find start and end of const digests array
    start_marker = 'const digests = ['
    end_marker = '];'

    start_idx = index_html.find(start_marker)
    if start_idx == -1:
        print("  ⚠ Could not find 'const digests' in index.html")
        return

    end_idx = index_html.find(end_marker, start_idx)
    if end_idx == -1:
        print("  ⚠ Could not find end of digests array")
        return

    # Build new HTML with updated digest list
    updated_html = (
        index_html[:start_idx] +
        f'const digests = {digests_js}' +
        index_html[end_idx + 1:]  # Keep the ]; part
    )

    index_path.write_text(updated_html, encoding='utf-8')


def main():
    """Main entry point."""
    print("=" * 70)
    print("Generating HTML Pages from Digests")
    print("=" * 70)

    # Find all digest markdown files
    output_dir = Path('output')
    digest_files = sorted(output_dir.glob('digest_*.md'), reverse=True)

    if not digest_files:
        print("\nNo digest files found in output directory.")
        return 1

    print(f"\nFound {len(digest_files)} digest file(s)")

    # Create converter
    converter = MarkdownToHTMLConverter()

    # Process each digest
    docs_dir = Path('docs')
    docs_dir.mkdir(exist_ok=True)

    digest_list = []

    for digest_file in digest_files:
        print(f"  Processing: {digest_file.name}")

        # Read markdown
        md_content = digest_file.read_text(encoding='utf-8')

        # Extract title and date
        title_match = re.search(r'^# (.+?)$', md_content, re.MULTILINE)
        title = title_match.group(1) if title_match else "APAC Legal Digest"

        date_match = re.search(r'digest_(\d{4}-\d{2}-\d{2})\.md', digest_file.name)
        date_str = date_match.group(1) if date_match else "unknown"

        # Convert to HTML
        html_content = converter.convert(md_content, title)

        # Save HTML file
        html_filename = digest_file.stem + '.html'
        html_path = docs_dir / html_filename
        html_path.write_text(html_content, encoding='utf-8')

        print(f"    → Generated: {html_filename}")

        # Add to digest list
        digest_list.append({
            'date': date_str,
            'title': title,
            'file': html_filename
        })

    # Update index.html with digest list
    print(f"\nUpdating index.html with {len(digest_list)} digest(s)...")
    index_path = docs_dir / 'index.html'

    if index_path.exists():
        update_index_with_digests(digest_list, index_path)
        print("  ✓ Index updated")
    else:
        print("  ⚠ index.html not found, skipping update")

    print("\n" + "=" * 70)
    print("HTML Generation Complete!")
    print("=" * 70)
    print(f"\nGenerated {len(digest_list)} HTML page(s) in docs/")
    print("View them at: https://mdh2321.github.io/legal-digest/")
    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
