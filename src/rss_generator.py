"""RSS 2.0 feed generator for legal news digest."""
import html
import re
from datetime import datetime
from email.utils import formatdate
from typing import List, Dict, Optional, Any
from .news_collector import NewsStory
from .config import ALL_JURISDICTIONS, TIER1_JURISDICTIONS, TIER2_JURISDICTIONS
from .date_utils import format_date_range
from .story_ranker import StoryRanker


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

    def _add_bold_emphasis(self, text: str) -> str:
        """
        Add bold emphasis to important legal/regulatory terms.

        Args:
            text: Text to process

        Returns:
            Text with key terms wrapped in <strong> tags
        """
        # Important terms to bold for scannability
        important_terms = [
            'compliance', 'mandatory', 'required', 'enforcement',
            'penalty', 'penalties', 'fine', 'fines',
            'deadline', 'effective date', 'implementation',
            'new law', 'new regulation', 'amendment',
            'data protection', 'privacy', 'AI governance',
            'cross-border', 'data transfer', 'consent',
            'notification', 'breach', 'incident response'
        ]

        result = text
        for term in important_terms:
            # Case-insensitive replacement, preserving original case
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            result = pattern.sub(lambda m: f'<strong>{m.group(0)}</strong>', result)

        return result

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

        Uses Claude-enhanced takeaways and summary when available,
        falling back to generic generation.

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

        # Use enhanced takeaways if available, else fall back to generated
        enhanced_takeaways = getattr(story, 'enhanced_takeaways', None)
        takeaways = enhanced_takeaways if enhanced_takeaways else self.generate_takeaways(story)

        # Use enhanced summary for relevance if available, else fall back
        enhanced_summary = getattr(story, 'enhanced_summary', None)
        relevance = enhanced_summary if enhanced_summary else self.generate_saas_relevance(story)

        categories = getattr(story, 'categories', [])

        # Build takeaways HTML
        takeaways_html = '\n'.join(f'          <li>{self.escape_xml(t)}</li>' for t in takeaways)

        # Get materiality label and source type
        materiality_label = StoryRanker.get_materiality_label(story)
        source_type = getattr(story, 'source_type', '')
        source_type_tag = f'[{source_type}]' if source_type else ''

        # Build categories XML
        category_xml = f'      <category>{self.escape_xml(jur_name)}</category>\n'
        for cat in categories[:3]:
            category_xml += f'      <category>{self.escape_xml(cat)}</category>\n'

        # Clean summary
        summary = enhanced_summary or story.summary or story.snippet
        if not summary:
            summary = "Details available at source."
        summary = summary.strip()

        # Source name
        source_name = story.source if story.source else 'Source'

        # Build content:encoded HTML with bold emphasis on key terms
        content_html = f"""<h2>Key Takeaways</h2>
        <ul>
{takeaways_html}
        </ul>
        <h2>Practical Impact</h2>
        <p>{self._add_bold_emphasis(self.escape_xml(relevance))}</p>
        <p><em>Country: <strong>{self.escape_xml(jur_name)}</strong> | Topics: {', '.join(f'<strong>{self.escape_xml(c)}</strong>' for c in categories[:3])}</em></p>
        <p><a href="{self.escape_xml(story.url)}">Read full article &rarr;</a></p>"""

        # Title with materiality label and source type
        title_prefix = f"{materiality_label} {source_type_tag} " if source_type_tag else f"{materiality_label} "
        title = self.escape_xml(title_prefix + story.title)

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
                      insights: str = "", deadlines: List = None,
                      ai_stories: List = None) -> str:
        """
        Generate complete RSS 2.0 feed.

        Args:
            selected_stories: Dict mapping jurisdiction codes to stories
            insights: Optional insights text (included as separate item)
            deadlines: List of compliance deadlines extracted from stories
            ai_stories: List of AI-related stories for the AI Tracker

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

        # Add Compliance Countdown section if deadlines exist
        if deadlines:
            countdown_item = self._format_compliance_countdown(deadlines)
            items_xml += '\n' + countdown_item

        # Add AI Regulatory Tracker section if AI stories exist
        if ai_stories:
            ai_tracker_item = self._format_ai_tracker(ai_stories)
            items_xml += '\n' + ai_tracker_item

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

    def _format_compliance_countdown(self, deadlines: List) -> str:
        """
        Format compliance deadlines as an RSS item.

        Args:
            deadlines: List of deadline dictionaries

        Returns:
            RSS item XML for compliance countdown
        """
        date_str = format_date_range(self.start_date, self.end_date)
        pub_date = self.to_rfc822_date(datetime.now())

        # Build deadline rows
        deadline_rows = []
        for d in deadlines[:10]:  # Limit to 10 upcoming deadlines
            jur_info = ALL_JURISDICTIONS.get(d['jurisdiction'], {})
            jur_name = jur_info.get('name', d['jurisdiction'])
            flag = jur_info.get('flag', '')

            # Calculate days until deadline
            days_until = (d['date'] - datetime.now()).days
            if days_until < 0:
                urgency = "past"
                days_text = f"{abs(days_until)} days ago"
            elif days_until == 0:
                urgency = "today"
                days_text = "TODAY"
            elif days_until <= 7:
                urgency = "urgent"
                days_text = f"{days_until} days"
            elif days_until <= 30:
                urgency = "soon"
                days_text = f"{days_until} days"
            else:
                urgency = "upcoming"
                days_text = f"{days_until} days"

            # Format date nicely
            date_formatted = d['date'].strftime('%d %b %Y')

            deadline_rows.append(f"""
            <tr style="border-bottom: 1px solid #eee;">
              <td style="padding: 8px; font-weight: bold; color: {'#dc2626' if urgency in ['today', 'urgent'] else '#92400e' if urgency == 'soon' else '#666'};">{days_text}</td>
              <td style="padding: 8px;">{date_formatted}</td>
              <td style="padding: 8px;">{flag} {self.escape_xml(jur_name)}</td>
              <td style="padding: 8px;">{self.escape_xml(d['description'])}</td>
            </tr>""")

        deadline_table = '\n'.join(deadline_rows) if deadline_rows else '<tr><td colspan="4">No upcoming deadlines identified this week.</td></tr>'

        content_html = f"""<h2>Compliance Countdown</h2>
        <p><em>Key regulatory deadlines affecting technology companies in APAC.</em></p>
        <table style="width: 100%; border-collapse: collapse; margin-top: 16px;">
          <thead>
            <tr style="background: #f5f0e8; text-align: left;">
              <th style="padding: 10px;">Time Left</th>
              <th style="padding: 10px;">Date</th>
              <th style="padding: 10px;">Jurisdiction</th>
              <th style="padding: 10px;">Requirement</th>
            </tr>
          </thead>
          <tbody>
            {deadline_table}
          </tbody>
        </table>
        <p style="margin-top: 16px; font-size: 0.9em; color: #666;"><em>Deadlines extracted from this week's stories. Verify all dates with primary sources.</em></p>"""

        return f"""    <item>
      <title>Compliance Countdown - {date_str}</title>
      <link>https://legal-digest.local/deadlines</link>
      <pubDate>{pub_date}</pubDate>
      <category>Deadlines</category>
      <category>Compliance</category>
      <description>Upcoming regulatory compliance deadlines for technology companies in APAC.</description>
      <content:encoded><![CDATA[
        {content_html}
      ]]></content:encoded>
    </item>"""

    def _format_ai_tracker(self, ai_stories: List[NewsStory]) -> str:
        """
        Format AI regulatory stories as an RSS item.

        Args:
            ai_stories: List of AI-related NewsStory objects

        Returns:
            RSS item XML for AI regulatory tracker
        """
        date_str = format_date_range(self.start_date, self.end_date)
        pub_date = self.to_rfc822_date(datetime.now())

        # Build story summaries
        story_items = []
        for story in ai_stories[:8]:  # Limit to 8 AI stories
            jur_info = ALL_JURISDICTIONS.get(story.jurisdiction, {})
            jur_name = jur_info.get('name', story.jurisdiction)
            flag = jur_info.get('flag', '')

            # Use enhanced summary if available
            summary = getattr(story, 'enhanced_summary', None) or story.summary or story.snippet
            summary = summary[:200] + '...' if len(summary) > 200 else summary

            story_items.append(f"""
            <div style="margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #eee;">
              <p style="margin: 0 0 4px 0;"><strong>{flag} {self.escape_xml(jur_name)}</strong></p>
              <p style="margin: 0 0 8px 0; font-weight: 600;">{self.escape_xml(story.title)}</p>
              <p style="margin: 0 0 8px 0; color: #666;">{self.escape_xml(summary)}</p>
              <p style="margin: 0;"><a href="{self.escape_xml(story.url)}">Read more &rarr;</a></p>
            </div>""")

        stories_html = '\n'.join(story_items) if story_items else '<p>No AI-specific regulatory developments identified this week.</p>'

        content_html = f"""<h2>AI Regulatory Tracker</h2>
        <p><em>This week's AI governance and regulation developments across all 10 APAC jurisdictions.</em></p>

        <div style="background: #f5f0e8; padding: 12px 16px; border-radius: 8px; margin: 16px 0;">
          <p style="margin: 0; font-size: 0.9em;"><strong>Coverage:</strong> Australia, Singapore, Japan, South Korea, India, Indonesia, Philippines, Hong Kong, New Zealand, Vietnam</p>
        </div>

        {stories_html}

        <p style="margin-top: 16px; font-size: 0.9em; color: #666;"><em>AI stories identified based on content analysis. Includes AI governance, algorithmic regulation, foundation models, and automated decision-making.</em></p>"""

        return f"""    <item>
      <title>AI Regulatory Tracker - {date_str}</title>
      <link>https://legal-digest.local/ai-tracker</link>
      <pubDate>{pub_date}</pubDate>
      <category>AI Regulation</category>
      <category>APAC</category>
      <description>AI governance and regulatory developments across 10 APAC jurisdictions.</description>
      <content:encoded><![CDATA[
        {content_html}
      ]]></content:encoded>
    </item>"""
