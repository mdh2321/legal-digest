"""News collection module using web search."""
import re
import time
from datetime import datetime
from typing import List, Dict, Optional
from html import unescape as html_unescape


class NewsStory:
    """Represents a single news story."""

    def __init__(self, title: str, url: str, source: str, date: datetime,
                 summary: str, jurisdiction: str, snippet: str = ""):
        self.title = title
        self.url = url
        self.source = source
        self.date = date
        self.summary = summary
        self.jurisdiction = jurisdiction
        self.snippet = snippet
        self.categories = []
        self.materiality_score = 0.0
        self.relevance_score = 0.0
        self.source_type = ""  # Regulator, Court, News, Law Firm, Publication

    def __repr__(self):
        return f"NewsStory(title={self.title[:50]}, jurisdiction={self.jurisdiction})"


class NewsCollector:
    """Collects legal news stories from web searches."""

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.stories = []

    def build_search_queries(self, jurisdiction: str) -> List[str]:
        """
        Build search queries for a jurisdiction from config keywords.

        Loops over DIGEST_SEARCH_KEYWORDS, prepending jurisdiction name.
        Also adds a regulator site search if available.

        Args:
            jurisdiction: Two-letter jurisdiction code

        Returns:
            List of search query strings
        """
        from .config import (
            ALL_JURISDICTIONS, REGULATOR_SOURCES, DIGEST_SEARCH_KEYWORDS
        )

        jur_info = ALL_JURISDICTIONS.get(jurisdiction)
        if not jur_info:
            return []
        jur_name = jur_info['name']

        queries = []

        # Keyword-driven queries from config
        for keyword in DIGEST_SEARCH_KEYWORDS:
            queries.append(f'{jur_name} {keyword}')

        # Regulator site search (if available)
        regulator_sites = REGULATOR_SOURCES.get(jurisdiction, [])
        if regulator_sites:
            batch = regulator_sites[:4]
            site_filter = ' OR '.join(f'site:{site}' for site in batch)
            queries.append(f'{jur_name} ({site_filter})')

        return queries

    def get_date_search_hint(self) -> str:
        """Get a date hint string for manual searches."""
        start_str = self.start_date.strftime('%d %B %Y')
        end_str = self.end_date.strftime('%d %B %Y')
        return f"Only include articles published between {start_str} and {end_str}"

    def clean_url(self, url: str) -> str:
        """Clean URL by removing tracking parameters."""
        tracking_params = ['utm_source', 'utm_medium', 'utm_campaign',
                           'utm_content', 'utm_term', 'fbclid', 'gclid']

        if '?' in url:
            base_url, params = url.split('?', 1)
            param_list = params.split('&')
            clean_params = [p for p in param_list
                            if not any(p.startswith(f'{tp}=') for tp in tracking_params)]
            if clean_params:
                return f"{base_url}?{'&'.join(clean_params)}"
            return base_url

        return url

    def extract_date_from_text(self, text: str) -> Optional[datetime]:
        """Extract date from text snippets."""
        patterns = [
            r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})',
            r'(\d{4})-(\d{2})-(\d{2})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    if '-' in match.group(0):
                        return datetime.strptime(match.group(0), '%Y-%m-%d')
                    else:
                        date_str = match.group(0)
                        for fmt in ['%d %B %Y', '%B %d, %Y', '%B %d %Y']:
                            try:
                                return datetime.strptime(date_str, fmt)
                            except ValueError:
                                continue
                except Exception:
                    continue

        return None

    @staticmethod
    def _strip_html(text: str) -> str:
        """Strip HTML tags and decode entities from text."""
        if not text:
            return text
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', text)
        # Decode HTML entities
        clean = html_unescape(clean)
        # Collapse whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    def _classify_source_type(self, url: str) -> str:
        """
        Classify a URL into a source type.

        Returns one of: Regulator, Court, Law Firm, Publication, News
        """
        from .config import (
            REGULATOR_SOURCES, COURT_SOURCES,
            LAW_FIRM_SOURCES, LEGAL_PUBLICATIONS
        )

        url_lower = url.lower()

        # Check regulator sources
        all_regulator_domains = []
        for sites in REGULATOR_SOURCES.values():
            all_regulator_domains.extend(sites)
        for domain in all_regulator_domains:
            if domain in url_lower:
                return "Regulator"

        # Check court sources
        for sites in COURT_SOURCES.values():
            for domain in sites:
                if domain in url_lower:
                    return "Court"

        # Check law firm sources
        for domain in LAW_FIRM_SOURCES:
            if domain in url_lower:
                return "Law Firm"

        # Check legal publications
        for domain in LEGAL_PUBLICATIONS:
            if domain in url_lower:
                return "Publication"

        return "News"

    def parse_search_results(self, results: List[Dict], jurisdiction: str) -> List[NewsStory]:
        """
        Parse search results into NewsStory objects.

        When a date is extractable from the snippet/title, it must fall within
        the target week. When no date is found, the story is still accepted
        (Brave's freshness=pw filter already limits to the past week).

        Args:
            results: List of search result dictionaries
            jurisdiction: Two-letter jurisdiction code

        Returns:
            List of NewsStory objects
        """
        stories = []

        for result in results:
            try:
                title = self._strip_html(result.get('title', ''))
                url = self.clean_url(result.get('url', ''))
                snippet = self._strip_html(result.get('snippet', ''))
                source = result.get('source', '')

                # Try to extract date from snippet/title
                date_obj = self.extract_date_from_text(snippet)
                if not date_obj:
                    date_obj = self.extract_date_from_text(title)
                if not date_obj:
                    # No date found — use end_date as proxy
                    date_obj = datetime.combine(self.end_date, datetime.min.time())

                story = NewsStory(
                    title=title,
                    url=url,
                    source=source,
                    date=date_obj,
                    summary=snippet,
                    jurisdiction=jurisdiction,
                    snippet=snippet
                )

                # Classify source type
                story.source_type = self._classify_source_type(url)

                stories.append(story)

            except Exception:
                continue

        return stories

    def collect_stories_for_jurisdiction(self, jurisdiction: str,
                                          search_function) -> List[NewsStory]:
        """
        Collect stories for a specific jurisdiction with retry logic.

        Args:
            jurisdiction: Two-letter jurisdiction code
            search_function: Function that performs web search

        Returns:
            List of NewsStory objects
        """
        queries = self.build_search_queries(jurisdiction)
        all_stories = []

        for query in queries:
            try:
                results = search_function(query)
                print(f"  [Search] '{query[:60]}...' -> {len(results)} results")
                stories = self.parse_search_results(results, jurisdiction)
                all_stories.extend(stories)
            except Exception as e:
                # Retry once with 2s backoff
                try:
                    time.sleep(2)
                    results = search_function(query)
                    stories = self.parse_search_results(results, jurisdiction)
                    all_stories.extend(stories)
                except Exception:
                    print(f"  [NewsCollector] Query failed after retry ({jurisdiction}): {query[:60]}...")
                    continue

        # Deduplicate by URL
        seen_urls = set()
        unique_stories = []
        for story in all_stories:
            if story.url not in seen_urls:
                seen_urls.add(story.url)
                unique_stories.append(story)

        return unique_stories

    def collect_all_stories(self, search_function) -> List[NewsStory]:
        """
        Collect stories from all jurisdictions plus extraterritorial searches.

        Args:
            search_function: Function that performs web search

        Returns:
            List of all NewsStory objects
        """
        from .config import ALL_JURISDICTIONS, EXTRATERRITORIAL_KEYWORDS

        all_stories = []

        # Standard jurisdiction searches
        for jur_code in ALL_JURISDICTIONS.keys():
            if jur_code == 'EXTRA':
                continue  # handled below
            stories = self.collect_stories_for_jurisdiction(jur_code, search_function)
            all_stories.extend(stories)

        # Extraterritorial searches (no jurisdiction prefix)
        extra_stories = []
        for keyword in EXTRATERRITORIAL_KEYWORDS:
            try:
                results = search_function(keyword)
                print(f"  [Search] EXTRA '{keyword[:60]}...' -> {len(results)} results")
                stories = self.parse_search_results(results, 'EXTRA')
                extra_stories.extend(stories)
            except Exception:
                try:
                    time.sleep(2)
                    results = search_function(keyword)
                    stories = self.parse_search_results(results, 'EXTRA')
                    extra_stories.extend(stories)
                except Exception:
                    print(f"  [NewsCollector] Extraterritorial query failed: {keyword[:60]}...")
                    continue

        # Deduplicate extraterritorial by URL
        seen_urls = {s.url for s in all_stories}
        for story in extra_stories:
            if story.url not in seen_urls:
                seen_urls.add(story.url)
                all_stories.append(story)

        self.stories = all_stories
        return all_stories
