"""LLM-powered content summarization and analysis using Claude."""
from typing import List, Dict, Optional
import os


class LLMSummarizer:
    """Generates summaries and analysis using Claude."""

    def __init__(self, use_claude: bool = True):
        """
        Initialize summarizer.

        Args:
            use_claude: Whether to use Claude API (if False, uses fallback methods)
        """
        self.use_claude = use_claude and self._has_claude_api()

    def _has_claude_api(self) -> bool:
        """Check if Claude API is available."""
        try:
            import anthropic
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            return api_key is not None
        except ImportError:
            return False

    def generate_story_summary(self, article_content: str, title: str = "",
                                max_words: int = 150) -> str:
        """
        Generate comprehensive summary of a story.

        Args:
            article_content: Full article text
            title: Article title
            max_words: Maximum words for summary

        Returns:
            Summary text
        """
        if self.use_claude:
            return self._claude_summarize(article_content, title, max_words)
        else:
            return self._fallback_summarize(article_content, max_words)

    def _claude_summarize(self, article_content: str, title: str, max_words: int) -> str:
        """Generate summary using Claude API."""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

            # Truncate content if too long
            max_content_chars = 3000
            content = article_content[:max_content_chars]

            prompt = f"""Summarize this legal/regulatory news article in 3-4 sentences ({max_words} words maximum).

Focus on:
1. What happened (new law, court ruling, regulatory action, enforcement, etc.)
2. Key details (scope, who is affected, timeline, requirements)
3. Practical implications for technology companies

Article title: {title}

Article content:
{content}

Provide a clear, factual summary that someone in a tech company's legal/compliance team would find useful. Do not include marketing language or opinions."""

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=250,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            summary = message.content[0].text.strip()

            # Ensure it ends with period
            if summary and not summary.endswith('.'):
                summary += '.'

            return summary

        except Exception as e:
            # Fallback if API call fails
            return self._fallback_summarize(article_content, max_words)

    def _fallback_summarize(self, content: str, max_words: int) -> str:
        """Generate summary without Claude API (extractive approach)."""
        if not content:
            return "Details available at source."

        # Take first few sentences
        sentences = content.split('.')
        summary_parts = []
        word_count = 0

        for sentence in sentences[:5]:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_words = len(sentence.split())
            if word_count + sentence_words <= max_words:
                summary_parts.append(sentence)
                word_count += sentence_words
            else:
                break

        if not summary_parts:
            # Just take first N words
            words = content.split()[:max_words]
            return ' '.join(words) + '...'

        summary = '. '.join(summary_parts) + '.'
        return summary

    def generate_why_it_matters(self, article_content: str, title: str,
                                  categories: List[str], jurisdiction: str) -> str:
        """
        Generate contextual "why it matters" statement.

        Args:
            article_content: Article text
            title: Article title
            categories: Relevant categories
            jurisdiction: Jurisdiction code

        Returns:
            Why it matters text (1-2 sentences)
        """
        if self.use_claude:
            return self._claude_why_it_matters(article_content, title, categories, jurisdiction)
        else:
            return self._fallback_why_it_matters(categories)

    def _claude_why_it_matters(self, article_content: str, title: str,
                                categories: List[str], jurisdiction: str) -> str:
        """Generate why it matters using Claude."""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

            # Truncate content
            content = article_content[:2000]

            from .config import ALL_JURISDICTIONS
            jurisdiction_name = ALL_JURISDICTIONS.get(jurisdiction, {}).get('name', jurisdiction)

            prompt = f"""For this {jurisdiction_name} legal/regulatory development, explain in 1-2 sentences why it matters to global technology companies operating in Asia-Pacific.

Focus on PRACTICAL business implications:
- Compliance requirements or changes
- Operational impacts
- Strategic considerations
- Deadlines or effective dates
- Cross-border implications

Article title: {title}
Categories: {', '.join(categories)}

Article excerpt:
{content}

Write 1-2 clear, actionable sentences starting with a verb (e.g., "Affects...", "Requires...", "Changes..."). Be specific and practical."""

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=150,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            why_it_matters = message.content[0].text.strip()

            # Ensure it ends with period
            if why_it_matters and not why_it_matters.endswith('.'):
                why_it_matters += '.'

            return why_it_matters

        except Exception as e:
            return self._fallback_why_it_matters(categories)

    def _fallback_why_it_matters(self, categories: List[str]) -> str:
        """Generate why it matters without Claude (template-based)."""
        if not categories:
            return "Affects regulatory compliance for technology operations."

        category_impacts = {
            'AI/ML': 'Impacts AI development, deployment, and governance strategies',
            'Data Privacy': 'Affects data handling, cross-border transfers, and privacy compliance obligations',
            'Cybersecurity': 'Influences security requirements, incident response, and breach notification duties',
            'Cloud': 'Impacts cloud service agreements, vendor management, and data residency',
            'eSignature': 'Affects digital transaction validity, authentication requirements, and contract formation',
            'Contract Law': 'Shapes commercial contracting practices and terms negotiation',
            'Competition': 'Impacts market strategy, M&A activities, and platform operations',
            'Consumer Protection': 'Affects customer-facing practices, disclosures, and terms of service',
            'Corporate Governance': 'Influences board oversight, reporting duties, and ESG compliance',
            'Fintech': 'Impacts digital financial service offerings and licensing requirements',
            'AML': 'Affects transaction monitoring, customer due diligence, and reporting obligations',
            'Anti-Bribery': 'Influences compliance programs, third-party due diligence, and risk assessments',
            'Outsourcing': 'Impacts vendor contracts, service delivery models, and data sharing'
        }

        # Use first matching category
        for category in categories:
            if category in category_impacts:
                return category_impacts[category] + '.'

        return "Affects regulatory compliance for technology operations."

    def generate_executive_summary(self, stories_by_jurisdiction: Dict,
                                     max_words: int = 200) -> str:
        """
        Generate executive summary for the entire digest.

        Args:
            stories_by_jurisdiction: Dict mapping jurisdiction to stories
            max_words: Maximum words

        Returns:
            Executive summary text
        """
        if self.use_claude:
            return self._claude_executive_summary(stories_by_jurisdiction, max_words)
        else:
            return self._fallback_executive_summary(stories_by_jurisdiction)

    def _claude_executive_summary(self, stories_by_jurisdiction: Dict, max_words: int) -> str:
        """Generate executive summary using Claude."""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

            # Collect story titles and summaries
            story_info = []
            for jur, stories in stories_by_jurisdiction.items():
                from .config import ALL_JURISDICTIONS
                jur_name = ALL_JURISDICTIONS.get(jur, {}).get('name', jur)
                for story in stories:
                    story_info.append(f"- {jur_name}: {story.title}")

            stories_text = '\n'.join(story_info[:15])  # Limit to first 15

            prompt = f"""Write a 2-3 paragraph executive summary ({max_words} words max) of this week's key legal and regulatory developments in Asia-Pacific for technology companies.

Stories covered this week:
{stories_text}

The summary should:
1. Highlight the most significant developments
2. Identify any regional trends or themes
3. Note cross-jurisdictional implications
4. Be written for a busy executive who wants the top-level overview

Write in clear, professional language. Focus on what matters most for technology companies operating in the region."""

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=350,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return message.content[0].text.strip()

        except Exception as e:
            return self._fallback_executive_summary(stories_by_jurisdiction)

    def _fallback_executive_summary(self, stories_by_jurisdiction: Dict) -> str:
        """Generate executive summary without Claude."""
        total_stories = sum(len(stories) for stories in stories_by_jurisdiction.values())
        jurisdictions = len(stories_by_jurisdiction)

        # Count categories
        from collections import Counter
        categories = Counter()
        for stories in stories_by_jurisdiction.values():
            for story in stories:
                categories.update(story.categories)

        top_categories = [cat for cat, count in categories.most_common(3)]

        summary = f"This week's digest covers {total_stories} significant legal and regulatory developments across {jurisdictions} Asia-Pacific jurisdictions. "

        if top_categories:
            summary += f"Key themes include {', '.join(top_categories[:2])} developments affecting technology companies in the region. "

        summary += "The developments highlight the evolving regulatory landscape for digital services, data protection, and technology governance across APJ markets."

        return summary

    def generate_cross_jurisdictional_analysis(self, stories_by_jurisdiction: Dict,
                                                max_words: int = 300) -> str:
        """
        Generate cross-jurisdictional analysis.

        Args:
            stories_by_jurisdiction: Dict mapping jurisdiction to stories
            max_words: Maximum words

        Returns:
            Analysis text
        """
        if self.use_claude:
            return self._claude_cross_jurisdictional(stories_by_jurisdiction, max_words)
        else:
            return self._fallback_cross_jurisdictional(stories_by_jurisdiction)

    def _claude_cross_jurisdictional(self, stories_by_jurisdiction: Dict, max_words: int) -> str:
        """Generate cross-jurisdictional analysis using Claude."""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

            # Collect story summaries
            story_summaries = []
            for jur, stories in stories_by_jurisdiction.items():
                from .config import ALL_JURISDICTIONS
                jur_name = ALL_JURISDICTIONS.get(jur, {}).get('name', jur)
                for story in stories:
                    categories_str = ', '.join(story.categories[:2])
                    story_summaries.append(f"{jur_name} ({categories_str}): {story.title}")

            stories_text = '\n'.join(story_summaries)

            prompt = f"""Analyze these legal/regulatory developments across Asia-Pacific and identify:

1. **Regional trends**: Common themes or convergent regulatory approaches
2. **Cross-border implications**: How developments in one jurisdiction might affect multinational operations
3. **Compliance considerations**: What tech companies should be aware of across the region

Stories:
{stories_text}

Write {max_words} words maximum. Use clear headings and bullet points. Focus on practical insights for tech companies operating across multiple APJ jurisdictions."""

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return message.content[0].text.strip()

        except Exception as e:
            return self._fallback_cross_jurisdictional(stories_by_jurisdiction)

    def _fallback_cross_jurisdictional(self, stories_by_jurisdiction: Dict) -> str:
        """Generate cross-jurisdictional analysis without Claude."""
        from collections import Counter

        # Analyze categories across jurisdictions
        category_by_jur = {}
        for jur, stories in stories_by_jurisdiction.items():
            cats = []
            for story in stories:
                cats.extend(story.categories)
            category_by_jur[jur] = set(cats)

        # Find common categories
        all_categories = Counter()
        for cats in category_by_jur.values():
            all_categories.update(cats)

        analysis = "### Regional Trends\n\n"

        # Identify trends
        common_cats = [cat for cat, count in all_categories.most_common(3) if count >= 2]
        if common_cats:
            analysis += f"- **{common_cats[0]} developments** emerging across multiple jurisdictions, indicating regional regulatory convergence\n"

        analysis += "\n### Cross-Border Implications\n\n"
        analysis += "- Technology companies operating across APJ jurisdictions should monitor these developments for compliance harmonization opportunities and potential conflicts\n"

        return analysis
