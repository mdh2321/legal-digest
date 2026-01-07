"""RSS 2.0 feed generator for legal news digest."""
import html
from datetime import datetime
from email.utils import formatdate
from typing import List, Dict, Optional
from .news_collector import NewsStory
from .config import ALL_JURISDICTIONS, TIER1_JURISDICTIONS, TIER2_JURISDICTIONS
from .date_utils import format_date_range


class RSSGenerator:
    """Generates RSS 2.0 feeds from digest stories."""

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def to_rfc822_date(self, dt: datetime) -> str:
        """
        Convert datetime to RFC 822 format for RSS.

        Args:
            dt: datetime object

        Returns:
            RFC 822 formatted date string
        """
        if hasattr(dt, 'timestamp'):
            return formatdate(dt.timestamp(), localtime=True)
        # Handle date objects
        dt_full = datetime.combine(dt, datetime.min.time())
        return formatdate(dt_full.timestamp(), localtime=True)

    def escape_xml(self, text: str) -> str:
        """
        Escape text for XML content.

        Args:
            text: Raw text

        Returns:
            XML-safe escaped text
        """
        if not text:
            return ""
        return html.escape(text, quote=True)

    def generate_saas_relevance(self, story: NewsStory) -> str:
        """
        Generate SaaS-specific relevance statement.

        Args:
            story: NewsStory object

        Returns:
            Relevance statement tailored for SaaS companies
        """
        category_impacts = {
            'AI/ML': 'Influences AI feature development, disclosure requirements, and liability frameworks for AI-powered services.',
            'Data Privacy': 'Affects customer data handling, DPA requirements, cross-border transfers, and data subject rights implementation.',
            'Cybersecurity': 'Impacts security architecture, incident response obligations, and customer notification requirements.',
            'Cloud': 'Affects service delivery models, data residency requirements, and cloud infrastructure compliance.',
            'eSignature': 'Impacts validity of electronically signed agreements, authentication requirements, and digital transaction workflows.',
            'Contract Law': 'Affects standard terms, limitation of liability clauses, auto-renewal provisions, and subscription agreements.',
            'Competition': 'Influences market strategy, platform practices, and potential regulatory scrutiny of digital services.',
            'Consumer Protection': 'Affects customer-facing practices, subscription disclosures, cancellation rights, and refund policies.',
            'Corporate Governance': 'Influences board oversight, ESG reporting, and corporate compliance obligations.',
            'Fintech': 'Impacts digital payment integrations, financial service partnerships, and regulatory licensing.',
            'AML': 'Affects customer verification processes, transaction monitoring, and compliance program requirements.',
            'Anti-Bribery': 'Influences partner due diligence, channel management, and compliance training requirements.',
            'Outsourcing': 'Affects vendor contracts, subprocessor requirements, and service delivery obligations.',
            'Tax': 'Impacts revenue recognition, transfer pricing, withholding obligations, and digital services tax exposure.'
        }

        categories = getattr(story, 'categories', [])
        if not categories:
            return 'May affect regulatory compliance for technology operations in this jurisdiction.'

        # Use first matching category
        for category in categories:
            if category in category_impacts:
                return category_impacts[category]

        return 'May affect regulatory compliance for technology operations in this jurisdiction.'

    def generate_takeaways(self, story: NewsStory) -> List[str]:
        """
        Generate key takeaways from story content.

        Args:
            story: NewsStory object

        Returns:
            List of 2-3 actionable takeaways
        """
        takeaways = []
        categories = getattr(story, 'categories', [])
        jurisdiction = story.jurisdiction
        jur_name = ALL_JURISDICTIONS.get(jurisdiction, {}).get('name', jurisdiction)

        # Generate category-specific takeaways
        category_takeaways = {
            'AI/ML': [
                f'Review AI governance frameworks for {jur_name} market requirements',
                'Assess disclosure obligations for AI-powered features',
                'Update AI risk assessment and documentation practices'
            ],
            'Data Privacy': [
                f'Review data handling practices for {jur_name} compliance',
                'Assess cross-border data transfer mechanisms',
                'Update privacy notices and consent workflows'
            ],
            'Cybersecurity': [
                f'Evaluate security controls against {jur_name} requirements',
                'Review incident response procedures and notification timelines',
                'Update security documentation and certifications'
            ],
            'Cloud': [
                f'Assess cloud service agreements for {jur_name} compliance',
                'Review data residency and sovereignty requirements',
                'Update customer-facing service terms if needed'
            ],
            'eSignature': [
                f'Verify electronic signature validity in {jur_name}',
                'Review authentication and identity verification processes',
                'Update signature workflows to meet local requirements'
            ],
            'Contract Law': [
                f'Review standard terms for {jur_name} enforceability',
                'Assess liability limitation and indemnification clauses',
                'Update subscription and renewal terms if affected'
            ],
            'Competition': [
                f'Monitor {jur_name} competition authority guidance',
                'Review platform practices and self-preferencing policies',
                'Assess market position and potential regulatory exposure'
            ],
            'Consumer Protection': [
                f'Review consumer-facing disclosures for {jur_name}',
                'Assess subscription cancellation and refund processes',
                'Update marketing claims and guarantee statements'
            ],
            'Tax': [
                f'Assess digital services tax exposure in {jur_name}',
                'Review transfer pricing documentation',
                'Update tax compliance and reporting procedures'
            ],
            'Outsourcing': [
                f'Review vendor contracts for {jur_name} requirements',
                'Assess subprocessor notification obligations',
                'Update due diligence and monitoring procedures'
            ]
        }

        # Get takeaways from first matching category
        for category in categories:
            if category in category_takeaways:
                takeaways = category_takeaways[category][:2]
                break

        # Add generic takeaway if none found
        if not takeaways:
            takeaways = [
                f'Monitor regulatory developments in {jur_name}',
                'Assess potential compliance obligations'
            ]

        return takeaways

    def format_item(self, story: NewsStory) -> str:
        """
        Format a single story as an RSS item.

        Args:
            story: NewsStory object

        Returns:
            RSS item XML string
        """
        # Get jurisdiction info
        jur_info = ALL_JURISDICTIONS.get(story.jurisdiction, {})
        jur_name = jur_info.get('name', story.jurisdiction)

        # Format pub date
        pub_date = self.to_rfc822_date(story.date)

        # Generate content
        takeaways = self.generate_takeaways(story)
        relevance = self.generate_saas_relevance(story)
        categories = getattr(story, 'categories', [])

        # Build takeaways HTML
        takeaways_html = '\n'.join(f'          <li>{self.escape_xml(t)}</li>' for t in takeaways)

        # Build categories XML
        category_xml = f'      <category>{self.escape_xml(jur_name)}</category>\n'
        for cat in categories[:3]:
            category_xml += f'      <category>{self.escape_xml(cat)}</category>\n'

        # Clean summary
        summary = story.summary if story.summary else story.snippet
        if not summary:
            summary = "Details available at source."
        summary = summary.strip()

        # Source name
        source_name = story.source if story.source else 'Source'

        # Build content:encoded HTML
        content_html = f"""<h2>Key Takeaways</h2>
        <ul>
{takeaways_html}
        </ul>
        <h2>Why This Matters for SaaS Companies</h2>
        <p>{self.escape_xml(relevance)}</p>
        <p><em>Country: {self.escape_xml(jur_name)} | Topics: {', '.join(self.escape_xml(c) for c in categories[:3])}</em></p>
        <p><a href="{self.escape_xml(story.url)}">Read full article &rarr;</a></p>"""

        # Escape title
        title = self.escape_xml(story.title)

        item_xml = f"""    <item>
      <title>{title}</title>
      <link>{self.escape_xml(story.url)}</link>
      <pubDate>{pub_date}</pubDate>
{category_xml.rstrip()}
      <description>{self.escape_xml(summary)}</description>
      <content:encoded><![CDATA[
        {content_html}
      ]]></content:encoded>
    </item>"""

        return item_xml

    def generate_feed(self, selected_stories: Dict[str, List[NewsStory]],
                      insights: str = "") -> str:
        """
        Generate complete RSS 2.0 feed.

        Args:
            selected_stories: Dict mapping jurisdiction codes to stories
            insights: Optional insights text (included as separate item)

        Returns:
            Complete RSS XML string
        """
        # Build date strings
        date_str = format_date_range(self.start_date, self.end_date)
        build_date = self.to_rfc822_date(datetime.now())

        # Collect all items in priority order
        items = []

        # Tier 1 jurisdictions first
        for jur_code in TIER1_JURISDICTIONS.keys():
            if jur_code in selected_stories:
                for story in selected_stories[jur_code]:
                    items.append(self.format_item(story))

        # Tier 2 jurisdictions
        for jur_code in TIER2_JURISDICTIONS.keys():
            if jur_code in selected_stories:
                for story in selected_stories[jur_code]:
                    items.append(self.format_item(story))

        # Join items
        items_xml = '\n'.join(items)

        # Add insights as final item if present
        if insights:
            insights_item = self._format_insights_item(insights)
            items_xml += '\n' + insights_item

        # Build complete feed
        feed_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>APAC Legal Digest - Week of {date_str}</title>
    <link>https://legal-digest.local/</link>
    <description>Weekly legal and regulatory news digest for global technology companies operating in Asia-Pacific. Covering Australia, Singapore, Japan, and other APAC jurisdictions.</description>
    <language>en</language>
    <lastBuildDate>{build_date}</lastBuildDate>
    <ttl>10080</ttl>
{items_xml}
  </channel>
</rss>"""

        return feed_xml

    def _format_insights_item(self, insights: str) -> str:
        """
        Format regional insights as an RSS item.

        Args:
            insights: Insights text

        Returns:
            RSS item XML for insights
        """
        date_str = format_date_range(self.start_date, self.end_date)
        pub_date = self.to_rfc822_date(datetime.now())

        content_html = f"""<h2>Regional Trends &amp; Analysis</h2>
        {self.escape_xml(insights).replace(chr(10), '<br/>')}
        <p><em>Analysis based on this week's regulatory developments across APAC.</em></p>"""

        return f"""    <item>
      <title>Region Insights - {date_str}</title>
      <link>https://legal-digest.local/insights</link>
      <pubDate>{pub_date}</pubDate>
      <category>Analysis</category>
      <category>APAC</category>
      <description>Cross-jurisdictional trends and upcoming regulatory developments for the week.</description>
      <content:encoded><![CDATA[
        {content_html}
      ]]></content:encoded>
    </item>"""
