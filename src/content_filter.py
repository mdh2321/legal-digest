"""Content filtering based on inclusion/exclusion rules."""
import re
from typing import List
from .news_collector import NewsStory
from urllib.parse import urlparse
from .config import EXCLUDE_TOPICS, INCLUDE_TOPICS, DOMAIN_BLOCKLIST, ALL_APPROVED_DOMAINS


class ContentFilter:
    """Filters news stories based on content rules."""

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def _extract_domain(self, url: str) -> str:
        """Extract the registered domain from a URL."""
        try:
            hostname = urlparse(url).hostname or ''
            return hostname.lower()
        except Exception:
            return ''

    def is_blocked_source(self, story: NewsStory) -> bool:
        """Check if story is from a blocked domain."""
        domain = self._extract_domain(story.url)
        for blocked in DOMAIN_BLOCKLIST:
            if domain.endswith(blocked) or blocked in domain:
                print(f"  [BLOCKED] '{story.title[:60]}...' from blocked domain: {domain}")
                return True
        return False

    def is_approved_source(self, story: NewsStory) -> bool:
        """Check if story URL matches any approved source domain."""
        domain = self._extract_domain(story.url)
        for approved in ALL_APPROVED_DOMAINS:
            if approved in domain or domain.endswith(approved):
                return True
        return False

    def should_exclude(self, story: NewsStory) -> bool:
        """
        Check if story should be excluded based on topic.

        Args:
            story: NewsStory object

        Returns:
            bool: True if story should be excluded
        """
        text = f"{story.title} {story.summary}".lower()

        for exclude_keyword in EXCLUDE_TOPICS:
            if exclude_keyword.lower() in text:
                print(f"  [EXCLUDE] '{story.title[:60]}...' matched '{exclude_keyword}'")
                return True

        return False

    def is_in_date_range(self, story: NewsStory) -> bool:
        """
        Check if story date is within target week (STRICT enforcement).

        This is a critical filter - only articles published within the
        exact target week (Monday-Sunday) should pass.

        Args:
            story: NewsStory object

        Returns:
            bool: True if date is strictly within the target week range
        """
        story_date = story.date.date()

        # Strict check: must be >= start_date AND <= end_date
        in_range = self.start_date <= story_date <= self.end_date

        # Log rejection for debugging
        if not in_range:
            print(f"  [DATE FILTER] Rejected: '{story.title[:50]}...' "
                  f"(date: {story_date}, range: {self.start_date} to {self.end_date})")

        return in_range

    def get_matching_categories(self, story: NewsStory) -> List[str]:
        """
        Get categories that match the story content.

        Args:
            story: NewsStory object

        Returns:
            List of matching category names
        """
        text = f"{story.title} {story.summary}".lower()
        matching = []

        for category, keywords in INCLUDE_TOPICS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    matching.append(category)
                    break  # Only add category once

        return matching

    def calculate_relevance_score(self, story: NewsStory) -> float:
        """
        Calculate how relevant the story is to tech law topics.

        Args:
            story: NewsStory object

        Returns:
            float: Relevance score (0.0 to 1.0)
        """
        categories = self.get_matching_categories(story)
        story.categories = categories

        if not categories:
            return 0.0

        # Base score from number of matching categories (no topic bias)
        base_score = min(len(categories) / 3.0, 1.0)

        return base_score

    def filter_stories(self, stories: List[NewsStory]) -> List[NewsStory]:
        """
        Filter stories based on all criteria.

        Args:
            stories: List of NewsStory objects

        Returns:
            List of filtered NewsStory objects
        """
        filtered = []

        for story in stories:
            # Check blocklist first
            if self.is_blocked_source(story):
                continue

            # Check source allowlist
            if not self.is_approved_source(story):
                domain = self._extract_domain(story.url)
                print(f"  [SOURCE] Rejected (unapproved domain: {domain}): '{story.title[:60]}...'")
                continue

            # Check exclusions
            if self.should_exclude(story):
                continue

            # Calculate relevance
            relevance = self.calculate_relevance_score(story)
            if relevance < 0.1:  # Minimum relevance threshold (lenient)
                print(f"  [RELEVANCE] Rejected (score={relevance:.2f}): '{story.title[:60]}...'")
                continue

            story.relevance_score = relevance
            filtered.append(story)

        return filtered

    def expand_acronyms(self, text: str) -> str:
        """
        Expand common acronyms on first use.

        Args:
            text: Text to process

        Returns:
            Text with acronyms expanded
        """
        acronym_map = {
            # Technology
            'AI': 'Artificial Intelligence (AI)',
            'ML': 'Machine Learning (ML)',
            'API': 'Application Programming Interface (API)',
            'SaaS': 'Software as a Service (SaaS)',
            'PaaS': 'Platform as a Service (PaaS)',
            'IaaS': 'Infrastructure as a Service (IaaS)',
            # Privacy & Data
            'GDPR': 'General Data Protection Regulation (GDPR)',
            'PDPA': 'Personal Data Protection Act (PDPA)',
            'PDPC': 'Personal Data Protection Commission (PDPC)',
            'PIPL': 'Personal Information Protection Law (PIPL)',
            'DPDP': 'Digital Personal Data Protection (DPDP)',
            'DPA': 'Data Protection Authority (DPA)',
            # Financial
            'AML': 'Anti-Money Laundering (AML)',
            'KYC': 'Know Your Customer (KYC)',
            'CFT': 'Counter Financing of Terrorism (CFT)',
            # Governance
            'ESG': 'Environmental, Social, and Governance (ESG)',
            # Australian Regulators
            'ACCC': 'Australian Competition and Consumer Commission (ACCC)',
            'ASIC': 'Australian Securities and Investments Commission (ASIC)',
            'OAIC': 'Office of the Australian Information Commissioner (OAIC)',
            'APRA': 'Australian Prudential Regulation Authority (APRA)',
            # Singapore Regulators
            'MAS': 'Monetary Authority of Singapore (MAS)',
            'IMDA': 'Infocomm Media Development Authority (IMDA)',
            # Japan Regulators
            'PPC': 'Personal Information Protection Commission (PPC)',
            'FSA': 'Financial Services Agency (FSA)',
            'METI': 'Ministry of Economy, Trade and Industry (METI)',
            # India Regulators
            'RBI': 'Reserve Bank of India (RBI)',
            'SEBI': 'Securities and Exchange Board of India (SEBI)',
            # Other
            'DST': 'Digital Services Tax (DST)',
            'B2B': 'Business-to-Business (B2B)',
            'B2C': 'Business-to-Consumer (B2C)'
        }

        result = text
        expanded = set()

        # Find acronyms in text
        for acronym, expansion in acronym_map.items():
            # Only expand first occurrence
            if acronym in text and acronym not in expanded:
                # Use word boundary to match whole words
                pattern = r'\b' + re.escape(acronym) + r'\b'
                result = re.sub(pattern, expansion, result, count=1)
                expanded.add(acronym)

        return result
