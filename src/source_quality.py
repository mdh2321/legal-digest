"""Source quality assessment and credibility scoring."""
import re
from typing import Tuple, Optional
from urllib.parse import urlparse


class SourceQualityScorer:
    """Assesses source credibility and quality."""

    def __init__(self):
        # Official government and regulatory domains by jurisdiction
        self.official_domains = {
            'AU': [
                'gov.au', 'legislation.gov.au', 'aph.gov.au',
                'accc.gov.au', 'asic.gov.au', 'oaic.gov.au', 'esafety.gov.au',
                'fedcourt.gov.au', 'hcourt.gov.au'
            ],
            'SG': [
                'gov.sg', 'mas.gov.sg', 'imda.gov.sg', 'pdpc.gov.sg',
                'csa.gov.sg', 'agc.gov.sg', 'parliament.gov.sg',
                'judiciary.gov.sg'
            ],
            'JP': [
                'go.jp', 'digital.go.jp', 'meti.go.jp', 'fsa.go.jp',
                'ppc.go.jp', 'courts.go.jp'
            ],
            'NZ': [
                'govt.nz', 'privacy.org.nz', 'legislation.govt.nz',
                'parliament.nz', 'courts.govt.nz'
            ],
            'HK': [
                'gov.hk', 'hkma.gov.hk', 'pcpd.org.hk', 'info.gov.hk',
                'judiciary.hk'
            ],
            'PH': [
                'gov.ph', 'bsp.gov.ph', 'dict.gov.ph', 'ntc.gov.ph'
            ],
            'VN': [
                'gov.vn', 'mic.gov.vn', 'sbv.gov.vn'
            ],
            'IN': [
                'gov.in', 'rbi.org.in', 'meity.gov.in', 'cert-in.org.in',
                'nic.in', 'indiancourts.nic.in'
            ]
        }

        # Major reputable news publications
        self.major_news_outlets = [
            # Australia
            'afr.com', 'theaustralian.com.au', 'smh.com.au', 'theage.com.au',
            'abc.net.au', 'sbs.com.au',
            # Singapore
            'straitstimes.com', 'businesstimes.com.sg', 'channelnewsasia.com',
            # Regional/International
            'reuters.com', 'bloomberg.com', 'ft.com', 'wsj.com',
            'nikkei.com', 'japantimes.co.jp', 'scmp.com',
            # India
            'economictimes.indiatimes.com', 'hindustanbusinessline.com',
            'livemint.com', 'thehindu.com'
        ]

        # Reputable legal publications and research organizations
        self.legal_publications = [
            'lexology.com', 'mondaq.com', 'iapp.org', 'law.com',
            'globallegalinsights.com', 'internationallawoffice.com',
            'asialaw.com', 'chambersandpartners.com'
        ]

        # Major law firms (credible but promotional)
        self.law_firm_patterns = [
            'allens', 'clayton', 'ashurst', 'minterellison', 'herbertsmith',
            'kingwood', 'rajah', 'tann', 'allenandgledhill', 'drewnapier',
            'whitecase', 'bakermckenzie', 'linklaters', 'cliffordchance',
            'freshfields', 'deloitte', 'pwc', 'kpmg', 'ey.com'
        ]

        # Content aggregators and low-quality sources
        self.aggregators = [
            'reddit.com', 'linkedin.com', 'facebook.com', 'twitter.com',
            'medium.com', 'substack.com', 'tumblr.com', 'wordpress.com',
            'blogspot.com', 'wix.com'
        ]

        # Paywall indicators
        self.paywall_indicators = [
            'subscriber-only', 'subscription required', 'paywall',
            'premium content', 'members only'
        ]

    def is_official_source(self, url: str, jurisdiction: str = None) -> bool:
        """
        Check if URL is from official government/regulatory source.

        Args:
            url: URL to check
            jurisdiction: Optional jurisdiction code to check against

        Returns:
            True if official source
        """
        domain = urlparse(url).netloc.lower()

        if jurisdiction and jurisdiction in self.official_domains:
            return any(d in domain for d in self.official_domains[jurisdiction])

        # Check all official domains
        all_official = [d for domains in self.official_domains.values() for d in domains]
        return any(d in domain for d in all_official)

    def is_major_news_outlet(self, url: str) -> bool:
        """Check if URL is from a major news publication."""
        domain = urlparse(url).netloc.lower()
        return any(outlet in domain for outlet in self.major_news_outlets)

    def is_legal_publication(self, url: str) -> bool:
        """Check if URL is from a legal publication."""
        domain = urlparse(url).netloc.lower()
        return any(pub in domain for pub in self.legal_publications)

    def is_law_firm(self, url: str) -> bool:
        """Check if URL is from a law firm website."""
        domain = urlparse(url).netloc.lower()
        url_lower = url.lower()
        return any(firm in url_lower for firm in self.law_firm_patterns)

    def is_aggregator(self, url: str) -> bool:
        """Check if URL is from a content aggregator."""
        domain = urlparse(url).netloc.lower()
        return any(agg in domain for agg in self.aggregators)

    def calculate_source_credibility(self, url: str, source_name: str,
                                      jurisdiction: str = None) -> float:
        """
        Calculate source credibility score.

        Args:
            url: Source URL
            source_name: Source name/publication
            jurisdiction: Optional jurisdiction code

        Returns:
            Credibility score from 0.0 (low) to 1.0 (high)
        """
        score = 0.5  # baseline

        # Official government/regulatory: highest credibility
        if self.is_official_source(url, jurisdiction):
            score = 1.0

        # Major news publication: high credibility
        elif self.is_major_news_outlet(url):
            score = 0.85

        # Legal publication: good credibility
        elif self.is_legal_publication(url):
            score = 0.75

        # Law firm: moderate credibility (may be promotional)
        elif self.is_law_firm(url):
            score = 0.6

        # Penalties for low-quality indicators
        if self.is_aggregator(url):
            score *= 0.3  # Major penalty

        # Boost for court decisions and legislation
        url_lower = url.lower()
        if any(term in url_lower for term in ['court', 'judgment', 'ruling', 'legislation', 'statute']):
            score = min(score * 1.2, 1.0)

        return max(0.0, min(1.0, score))

    def get_source_tier(self, url: str, jurisdiction: str = None) -> int:
        """
        Get source tier (1=best, 3=lowest acceptable).

        Args:
            url: Source URL
            jurisdiction: Optional jurisdiction code

        Returns:
            Tier number (1, 2, or 3)
        """
        if self.is_official_source(url, jurisdiction):
            return 1
        elif self.is_major_news_outlet(url):
            return 2
        elif self.is_legal_publication(url) or self.is_law_firm(url):
            return 3
        else:
            return 3  # Default to tier 3

    def is_acceptable_source(self, url: str) -> bool:
        """
        Check if source meets minimum quality standards.

        Args:
            url: Source URL

        Returns:
            True if acceptable
        """
        # Reject aggregators
        if self.is_aggregator(url):
            return False

        # Reject obviously promotional or low-quality domains
        domain = urlparse(url).netloc.lower()
        rejected_patterns = [
            'prweb.com', 'prnewswire.com', 'businesswire.com',
            'marketwatch.com/press-release'
        ]
        if any(pattern in domain for pattern in rejected_patterns):
            return False

        return True

    def get_quality_summary(self, url: str, source_name: str,
                             jurisdiction: str = None) -> dict:
        """
        Get comprehensive quality assessment.

        Args:
            url: Source URL
            source_name: Source name
            jurisdiction: Optional jurisdiction code

        Returns:
            Dict with quality metrics
        """
        return {
            'credibility_score': self.calculate_source_credibility(url, source_name, jurisdiction),
            'tier': self.get_source_tier(url, jurisdiction),
            'is_official': self.is_official_source(url, jurisdiction),
            'is_news': self.is_major_news_outlet(url),
            'is_legal': self.is_legal_publication(url),
            'is_acceptable': self.is_acceptable_source(url),
            'source_type': self._get_source_type(url, jurisdiction)
        }

    def _get_source_type(self, url: str, jurisdiction: str = None) -> str:
        """Get human-readable source type."""
        if self.is_official_source(url, jurisdiction):
            return 'Official/Regulatory'
        elif self.is_major_news_outlet(url):
            return 'Major News'
        elif self.is_legal_publication(url):
            return 'Legal Publication'
        elif self.is_law_firm(url):
            return 'Law Firm'
        else:
            return 'Other'
