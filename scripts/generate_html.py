#!/usr/bin/env python3
"""
Generate digest.html from the RSS feed.xml.

Parses the RSS XML and renders a styled HTML page matching the
existing digest.html design.
"""
import re
import html
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path


def parse_feed(feed_path: str) -> dict:
    """Parse feed.xml and extract stories, deadlines, insights."""
    tree = ET.parse(feed_path)
    root = tree.getroot()

    ns = {'content': 'http://purl.org/rss/1.0/modules/content/'}
    channel = root.find('channel')
    title = channel.findtext('title', '')

    # Extract week date from title: "APAC Legal Digest - Week of ..."
    week_match = re.search(r'Week of (.+)', title)
    week_str = week_match.group(1) if week_match else ''

    stories = []
    deadlines_html = ''
    ai_tracker_html = ''
    insights_html = ''

    for item in channel.findall('item'):
        item_title = item.findtext('title', '')
        link = item.findtext('link', '')
        description = item.findtext('description', '')
        content_encoded = item.findtext('content:encoded', '', ns)
        categories = [c.text for c in item.findall('category') if c.text]

        # Classify special sections
        if 'Compliance Countdown' in item_title:
            deadlines_html = content_encoded
            continue
        elif 'AI Regulatory Tracker' in item_title:
            ai_tracker_html = content_encoded
            continue
        elif 'Region Insights' in item_title:
            insights_html = content_encoded
            continue

        # Parse materiality tag from title
        materiality = ''
        source_type = ''
        clean_title = item_title

        tag_pattern = r'\[(NEW LAW|ENFORCEMENT|COURT DECISION|CONSULTATION|GUIDANCE|ANALYSIS)\]'
        m = re.search(tag_pattern, item_title)
        if m:
            materiality = m.group(1).lower().replace(' ', '-')
            clean_title = re.sub(tag_pattern, '', clean_title).strip()

        src_pattern = r'\[(Regulator|Court|News|Law Firm|Publication)\]'
        m2 = re.search(src_pattern, clean_title)
        if m2:
            source_type = m2.group(1)
            clean_title = re.sub(src_pattern, '', clean_title).strip()

        # Extract takeaways from content:encoded
        takeaways = []
        takeaway_matches = re.findall(r'<li>(.*?)</li>', content_encoded)
        for t in takeaway_matches:
            takeaways.append(html.unescape(re.sub(r'<[^>]+>', '', t)))

        # Extract relevance/practical impact
        relevance = ''
        rel_match = re.search(r'<h2>Practical Impact</h2>\s*<p>(.*?)</p>', content_encoded, re.DOTALL)
        if rel_match:
            relevance = html.unescape(re.sub(r'<[^>]+>', '', rel_match.group(1)))

        # Determine jurisdiction from categories
        jurisdiction = categories[0] if categories else ''
        topic_cats = categories[1:4] if len(categories) > 1 else []

        stories.append({
            'title': clean_title,
            'link': link,
            'description': html.unescape(description),
            'jurisdiction': jurisdiction,
            'categories': topic_cats,
            'materiality': materiality,
            'source_type': source_type,
            'takeaways': takeaways,
            'relevance': relevance,
        })

    return {
        'week_str': week_str,
        'stories': stories,
        'deadlines_html': deadlines_html,
        'ai_tracker_html': ai_tracker_html,
        'insights_html': insights_html,
    }


def get_tag_class(materiality: str) -> str:
    """Map materiality label to CSS class."""
    mapping = {
        'new-law': 'new-law',
        'enforcement': 'enforcement',
        'court-decision': 'enforcement',
        'consultation': 'deadline',
        'guidance': '',
        'analysis': '',
    }
    return mapping.get(materiality, '')


def get_jurisdiction_flag(name: str) -> str:
    """Get flag emoji for jurisdiction name."""
    flags = {
        'Australia': '&#127462;&#127482;',
        'Singapore': '&#127480;&#127468;',
        'Japan': '&#127471;&#127477;',
        'India': '&#127470;&#127475;',
        'South Korea': '&#127472;&#127479;',
        'Hong Kong': '&#127469;&#127472;',
        'New Zealand': '&#127475;&#127487;',
        'Indonesia': '&#127470;&#127465;',
        'Philippines': '&#127477;&#127469;',
        'Vietnam': '&#127483;&#127475;',
        'Malaysia': '&#127474;&#127486;',
        'Taiwan': '&#127481;&#127484;',
        'Thailand': '&#127481;&#127469;',
        'ASEAN': '&#127758;',
        'APAC': '&#127758;',
    }
    return flags.get(name, '&#127758;')


def render_story(story: dict, index: int) -> str:
    """Render a single story as HTML."""
    flag = get_jurisdiction_flag(story['jurisdiction'])
    tag_class = get_tag_class(story['materiality'])
    materiality_label = story['materiality'].replace('-', ' ').title() if story['materiality'] else ''

    tags_html = ''
    if materiality_label:
        cls = f' {tag_class}' if tag_class else ''
        tags_html += f'<span class="tag{cls}">{html.escape(materiality_label)}</span>\n'
    if story['source_type']:
        tags_html += f'<span class="tag">{html.escape(story["source_type"])}</span>\n'
    for cat in story['categories']:
        cat_class = ' ai' if cat in ('AI/ML',) else ''
        tags_html += f'<span class="tag{cat_class}">{html.escape(cat)}</span>\n'

    takeaways_html = ''
    if story['takeaways']:
        items = '\n'.join(f'<li>{html.escape(t)}</li>' for t in story['takeaways'][:3])
        takeaways_html = f"""
                    <div class="takeaways">
                        <p class="takeaways-label">What This Means for You</p>
                        <ul>
                            {items}
                        </ul>
                    </div>"""

    return f"""
                <article class="story">
                    <span class="story-number">{index}</span>
                    <p class="story-jurisdiction"><span class="flag">{flag}</span> {html.escape(story['jurisdiction'])}</p>
                    <h2 class="story-title"><a href="{html.escape(story['link'])}">{html.escape(story['title'])}</a></h2>
                    <div class="story-tags">
                        {tags_html.strip()}
                    </div>
                    <p class="story-summary">
                        {html.escape(story['description'])}
                    </p>{takeaways_html}
                </article>"""


def render_html(data: dict) -> str:
    """Render the full digest HTML page."""
    week_str = data['week_str']
    now_str = datetime.now().strftime('%B %d, %Y')

    # Render stories
    stories_html = ''
    for i, story in enumerate(data['stories'], 1):
        stories_html += render_story(story, i)

    # Deadlines section
    deadlines_section = ''
    if data['deadlines_html']:
        deadlines_section = f"""
            <section class="compliance-countdown">
                <p class="section-label">Compliance Countdown</p>
                {data['deadlines_html']}
            </section>"""

    # Insights section
    insights_section = ''
    if data['insights_html']:
        insights_section = f"""
            <section class="stories">
                <p class="section-label">Region Insights</p>
                <div style="padding: 1.5rem 0;">
                    {data['insights_html']}
                </div>
            </section>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APAC Legal Digest - Week of {html.escape(week_str)}</title>
    <link rel="alternate" type="application/rss+xml" title="APAC Legal Digest" href="feed.xml">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        :root {{
            --bg-primary: #ffffff;
            --bg-secondary: #f3f5fa;
            --bg-accent: #eef2ff;
            --text-primary: #16181d;
            --text-secondary: #4b5565;
            --text-muted: #6c7382;
            --accent: #4f46e5;
            --accent-dark: #3730a3;
            --border: #d9dfeb;
            --link: #1f2937;
            --shadow-soft: 0 12px 34px rgba(22, 24, 29, 0.08);
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background:
                radial-gradient(circle at 5% 0%, #e0e7ff 0, transparent 35%),
                radial-gradient(circle at 100% 100%, #dbeafe 0, transparent 28%),
                var(--bg-secondary);
            color: var(--text-primary);
            line-height: 1.6;
            font-size: 16px;
            -webkit-font-smoothing: antialiased;
            padding: 2rem 1rem;
        }}

        .container {{
            max-width: 760px;
            margin: 0 auto;
            background: var(--bg-primary);
            min-height: calc(100vh - 4rem);
            border: 1px solid rgba(255, 255, 255, 0.8);
            border-radius: 24px;
            box-shadow: var(--shadow-soft);
            overflow: hidden;
        }}

        header {{
            padding: 2.5rem 2rem 2rem;
            border-bottom: 1px solid var(--border);
            background: linear-gradient(160deg, #ffffff 0%, #f8faff 100%);
        }}

        .brand {{ display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem; }}
        .brand-icon {{ width: 42px; height: 42px; background: linear-gradient(135deg, var(--accent) 0%, #60a5fa 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; color: #fff; box-shadow: 0 8px 18px rgba(79, 70, 229, 0.28); }}
        .brand-text {{ font-size: 1.125rem; font-weight: 700; letter-spacing: -0.02em; }}
        .edition {{ font-size: 0.875rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }}
        h1 {{ font-size: 2rem; font-weight: 700; letter-spacing: -0.03em; line-height: 1.2; }}
        .nav-links {{ margin-top: 1.25rem; display: flex; gap: 1.5rem; }}
        .nav-links a {{ color: var(--text-secondary); text-decoration: none; font-size: 0.875rem; font-weight: 500; padding: 0.35rem 0.7rem; border-radius: 999px; border: 1px solid transparent; transition: color 0.15s, border-color 0.15s, background 0.15s; }}
        .nav-links a:hover {{ color: var(--text-primary); border-color: var(--border); background: #fff; }}

        main {{ padding: 0 2rem; }}

        .section-label {{ font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent-dark); margin-bottom: 1rem; }}

        .stories {{ padding: 2rem 0; }}
        .story {{ padding: 2rem 0; border-bottom: 1px solid var(--border); transition: transform 0.15s ease, box-shadow 0.15s ease; border-radius: 12px; padding-left: 1rem; padding-right: 1rem; margin-left: -1rem; margin-right: -1rem; }}
        .story:last-child {{ border-bottom: none; }}
        .story:hover {{ transform: translateY(-2px); box-shadow: 0 10px 22px rgba(22, 24, 29, 0.06); }}

        .story-number {{ display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; background: linear-gradient(135deg, var(--accent) 0%, #2563eb 100%); color: white; font-size: 0.875rem; font-weight: 600; border-radius: 50%; margin-bottom: 1rem; }}
        .story-jurisdiction {{ display: inline-flex; align-items: center; gap: 0.5rem; font-size: 0.8125rem; font-weight: 500; color: var(--accent-dark); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem; }}
        .story-jurisdiction .flag {{ font-size: 1rem; }}
        .story-title {{ font-size: 1.35rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.3; margin-bottom: 0.5rem; }}
        .story-title a {{ color: inherit; text-decoration: none; }}
        .story-title a:hover {{ text-decoration: underline; }}
        .story-tags {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.25rem; }}
        .tag {{ font-size: 0.6875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; padding: 0.25rem 0.625rem; border-radius: 4px; background: var(--bg-secondary); color: var(--text-secondary); }}
        .tag.enforcement {{ background: #fef2f2; color: #991b1b; }}
        .tag.deadline {{ background: #fef3c7; color: #92400e; }}
        .tag.new-law {{ background: #ecfdf5; color: #065f46; }}
        .tag.ai {{ background: #ede9fe; color: #5b21b6; }}
        .story-summary {{ font-size: 1rem; color: var(--text-secondary); line-height: 1.7; margin-bottom: 1.5rem; }}
        .story-summary strong {{ color: var(--text-primary); font-weight: 600; }}

        .takeaways {{ background: #f6f8ff; border-left: 3px solid var(--accent); padding: 1.25rem 1.25rem 1.25rem 1.5rem; border-radius: 0 8px 8px 0; margin-bottom: 1.25rem; }}
        .takeaways-label {{ font-size: 0.6875rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent-dark); margin-bottom: 0.75rem; }}
        .takeaways ul {{ list-style: none; }}
        .takeaways li {{ font-size: 0.9375rem; color: var(--text-secondary); padding: 0.375rem 0; padding-left: 1.25rem; position: relative; }}
        .takeaways li::before {{ content: "→"; position: absolute; left: 0; color: var(--accent); font-weight: 600; }}

        .compliance-countdown {{ padding: 2rem 0; border-bottom: 1px solid var(--border); }}
        .compliance-countdown table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        .compliance-countdown th {{ background: #f3f4ff; padding: 0.75rem; text-align: left; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }}
        .compliance-countdown td {{ padding: 0.75rem; border-bottom: 1px solid var(--border); font-size: 0.9375rem; }}

        footer {{ padding: 2.5rem 2rem; border-top: 1px solid var(--border); text-align: center; background: #fcfdff; }}
        .footer-brand {{ font-weight: 600; margin-bottom: 0.5rem; }}
        .footer-meta {{ font-size: 0.875rem; color: var(--text-muted); }}

        @media (max-width: 640px) {{
            body {{ padding: 0; }}
            .container {{ min-height: 100vh; border-radius: 0; border: none; box-shadow: none; }}
            header, main, footer {{ padding-left: 1.25rem; padding-right: 1.25rem; }}
            h1 {{ font-size: 1.625rem; }}
            .story-title {{ font-size: 1.125rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">
                <div class="brand-icon">&#9878;</div>
                <span class="brand-text">APAC Legal Digest</span>
            </div>
            <p class="edition">Week of {html.escape(week_str)}</p>
            <h1>Tech Law Developments Across Asia-Pacific</h1>
            <nav class="nav-links">
                <a href="index.html">&larr; Home</a>
                <a href="archive.html">Archive</a>
                <a href="feed.xml">Subscribe via RSS</a>
            </nav>
        </header>

        <main>
            <section class="stories">
                <p class="section-label">This Week's Stories</p>
                {stories_html}
            </section>
{deadlines_section}
{insights_section}
        </main>

        <footer>
            <p class="footer-brand">APAC Legal Digest</p>
            <p class="footer-meta">For technology company legal professionals</p>
            <p class="footer-meta">Generated {html.escape(now_str)}</p>
        </footer>
    </div>
</body>
</html>"""


def main():
    project_root = Path(__file__).parent.parent
    feed_path = project_root / 'docs' / 'feed.xml'
    output_path = project_root / 'docs' / 'digest.html'

    if not feed_path.exists():
        print("No feed.xml found in docs/")
        return

    data = parse_feed(str(feed_path))
    html_content = render_html(data)
    output_path.write_text(html_content)
    print(f"Generated digest.html with {len(data['stories'])} stories")


if __name__ == '__main__':
    main()
