#!/usr/bin/env python3
"""
Update the archive index page with list of all historical digests.
"""
import os
import re
from pathlib import Path
from datetime import datetime


def get_digest_files(archive_dir: Path) -> list:
    """Get all digest files sorted by date (newest first)."""
    files = []
    for f in archive_dir.glob('digest-*.html'):
        # Extract date from filename: digest-YYYY-MM-DD.html
        match = re.search(r'digest-(\d{4}-\d{2}-\d{2})\.html', f.name)
        if match:
            date_str = match.group(1)
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                files.append({
                    'filename': f.name,
                    'date': date,
                    'date_str': date.strftime('%d %B %Y'),
                    'week_str': f"Week of {date.strftime('%d %B %Y')}"
                })
            except ValueError:
                continue

    # Sort by date, newest first
    files.sort(key=lambda x: x['date'], reverse=True)
    return files


def generate_archive_html(files: list) -> str:
    """Generate the archive index HTML page."""
    # Build file list HTML
    if files:
        file_items = []
        for f in files:
            file_items.append(f'''
                <li class="archive-item">
                    <a href="archive/{f['filename']}">{f['week_str']}</a>
                    <span class="archive-date">{f['date_str']}</span>
                </li>''')
        file_list = '\n'.join(file_items)
    else:
        file_list = '<li class="archive-item">No archived digests yet.</li>'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APAC Legal Digest - Archive</title>
    <link rel="alternate" type="application/rss+xml" title="APAC Legal Digest" href="feed.xml">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        :root {{
            --bg-primary: #ffffff;
            --bg-secondary: #faf8f5;
            --bg-accent: #f5f0e8;
            --text-primary: #1a1a1a;
            --text-secondary: #5c5c5c;
            --text-muted: #8a8a8a;
            --accent: #c9a227;
            --accent-dark: #a68521;
            --border: #e8e4dc;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-secondary);
            color: var(--text-primary);
            line-height: 1.6;
            font-size: 16px;
            -webkit-font-smoothing: antialiased;
            min-height: 100vh;
            padding: 2rem 1rem;
        }}

        .container {{
            max-width: 680px;
            margin: 0 auto;
            background: var(--bg-primary);
            border-radius: 16px;
            padding: 2.5rem;
            box-shadow: 0 4px 24px rgba(0,0,0,0.06);
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
        }}

        .brand-icon {{
            width: 40px;
            height: 40px;
            background: var(--accent);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
        }}

        .brand-text {{
            font-size: 1.125rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }}

        h1 {{
            font-size: 1.75rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}

        .subtitle {{
            color: var(--text-secondary);
            margin-bottom: 2rem;
        }}

        .nav-links {{
            display: flex;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .nav-links a {{
            color: var(--text-muted);
            text-decoration: none;
            font-size: 0.875rem;
            font-weight: 500;
        }}

        .nav-links a:hover {{
            color: var(--text-primary);
        }}

        .archive-list {{
            list-style: none;
        }}

        .archive-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 0;
            border-bottom: 1px solid var(--border);
        }}

        .archive-item:last-child {{
            border-bottom: none;
        }}

        .archive-item a {{
            color: var(--text-primary);
            text-decoration: none;
            font-weight: 500;
        }}

        .archive-item a:hover {{
            color: var(--accent-dark);
        }}

        .archive-date {{
            color: var(--text-muted);
            font-size: 0.875rem;
        }}

        .info-box {{
            background: var(--bg-accent);
            border-radius: 8px;
            padding: 1rem;
            margin-top: 2rem;
            font-size: 0.875rem;
            color: var(--text-secondary);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="brand">
            <div class="brand-icon">&#9878;</div>
            <span class="brand-text">APAC Legal Digest</span>
        </div>

        <h1>Archive</h1>
        <p class="subtitle">Previous weekly digests (last 12 weeks)</p>

        <nav class="nav-links">
            <a href="index.html">&larr; Home</a>
            <a href="digest.html">Current Issue</a>
            <a href="feed.xml">RSS Feed</a>
        </nav>

        <ul class="archive-list">
            {file_list}
        </ul>

        <div class="info-box">
            Archives are retained for 12 weeks. For older content, please contact us or check the RSS feed history in your reader.
        </div>
    </div>
</body>
</html>'''


def main():
    """Main function to update archive index."""
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    docs_dir = project_root / 'docs'
    archive_dir = docs_dir / 'archive'

    # Ensure archive directory exists
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Get digest files
    files = get_digest_files(archive_dir)

    # Generate and write archive index
    html = generate_archive_html(files)
    archive_index = docs_dir / 'archive.html'
    archive_index.write_text(html)

    print(f"Updated archive index with {len(files)} digests")


if __name__ == '__main__':
    main()
