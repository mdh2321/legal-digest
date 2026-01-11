"""News collection module using web search."""
import re
from datetime import datetime
from typing import List, Dict, Optional


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
        Build comprehensive search queries for a jurisdiction.

        Searches across:
        - General web for topic + jurisdiction + date
        - Jurisdiction-specific regulator sites
        - Major law firm publications
        - Legal news aggregators

        Args:
            jurisdiction: Two-letter jurisdiction code

        Returns:
            List of search query strings
        """
        from .config import (
            ALL_JURISDICTIONS, REGULATOR_SOURCES,
            LAW_FIRM_SOURCES, LEGAL_PUBLICATIONS
        )

        jur_name = ALL_JURISDICTIONS[jurisdiction]['name']
        year = self.end_date.year
        month = self.end_date.strftime('%B')  # e.g., "January"

        queries = []

        # --- 1. TOPIC-BASED SEARCHES ---
        topics = [
            'data privacy law',
            'cybersecurity regulation',
            'artificial intelligence law',
            'digital regulation',
            'fintech law',
            'technology regulation',
        ]

        for topic in topics:
            queries.append(f'{jur_name} {topic} {month} {year}')

        # --- 2. REGULATOR-SPECIFIC SEARCHES ---
        regulator_sites = REGULATOR_SOURCES.get(jurisdiction, [])
        if regulator_sites:
            # Create site: query for regulators
            site_filter = ' OR '.join(f'site:{site}' for site in regulator_sites[:4])
            queries.append(f'{jur_name} regulation announcement {month} {year} ({site_filter})')

        # --- 3. LAW FIRM PUBLICATION SEARCHES ---
        # Search major law firm sites for jurisdiction-specific updates
        top_firms = LAW_FIRM_SOURCES[:10]  # Top 10 global firms
        firm_filter = ' OR '.join(f'site:{firm}' for firm in top_firms)
        queries.append(f'{jur_name} legal update {month} {year} ({firm_filter})')

        # --- 4. LEGAL PUBLICATION SEARCHES ---
        # Search legal news aggregators
        top_pubs = ['lexology.com', 'mondaq.com', 'iapp.org', 'law360.com']
        pub_filter = ' OR '.join(f'site:{pub}' for pub in top_pubs)
        queries.append(f'{jur_name} privacy data AI law {month} {year} ({pub_filter})')

        return queries

    def build_law_firm_queries(self) -> List[str]:
        """
        Build queries specifically targeting law firm publications.

        Returns:
            List of search query strings for law firm content
        """
        from .config import LAW_FIRM_SOURCES

        year = self.end_date.year
        month = self.end_date.strftime('%B')

        queries = []

        # Group firms into batches for OR queries
        batch_size = 5
        topics = ['data privacy', 'AI regulation', 'technology law']

        for i in range(0, min(len(LAW_FIRM_SOURCES), 25), batch_size):
            batch = LAW_FIRM_SOURCES[i:i + batch_size]
            site_filter = ' OR '.join(f'site:{firm}' for firm in batch)
            for topic in topics:
                queries.append(f'Asia Pacific {topic} {month} {year} ({site_filter})')

        return queries

    def build_publication_queries(self) -> List[str]:
        """
        Build queries specifically targeting legal publications.

        Returns:
            List of search query strings for legal publications
        """
        from .config import LEGAL_PUBLICATIONS

        year = self.end_date.year
        month = self.end_date.strftime('%B')

        queries = []

        # Key aggregators
        key_pubs = ['lexology.com', 'mondaq.com', 'iapp.org', 'law360.com', 'iclg.com']
        site_filter = ' OR '.join(f'site:{pub}' for pub in key_pubs)

        jurisdictions = ['Australia', 'Singapore', 'Japan', 'India', 'Korea', 'Hong Kong']
        for jur in jurisdictions:
            queries.append(f'{jur} data privacy technology law {month} {year} ({site_filter})')

        return queries

    def get_date_search_hint(self) -> str:
        """
        Get a date hint string for manual searches.

        Returns:
            String describing the target date range
        """
        start_str = self.start_date.strftime('%d %B %Y')
        end_str = self.end_date.strftime('%d %B %Y')
        return f"Only include articles published between {start_str} and {end_str}"

    def clean_url(self, url: str) -> str:
        """
        Clean URL by removing tracking parameters.

        Args:
            url: Raw URL

        Returns:
            Cleaned URL
        """
        # Remove common tracking parameters
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
        """
        Extract date from text snippets.

        Args:
            text: Text containing potential date

        Returns:
            datetime object or None
        """
        # Common date patterns
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
                        # Try to parse the matched date
                        date_str = match.group(0)
                        for fmt in ['%d %B %Y', '%B %d, %Y', '%B %d %Y']:
                            try:
                                return datetime.strptime(date_str, fmt)
                            except ValueError:
                                continue
                except Exception:
                    continue

        return None

    def parse_search_results(self, results: List[Dict], jurisdiction: str) -> List[NewsStory]:
        """
        Parse search results into NewsStory objects.

        Args:
            results: List of search result dictionaries
            jurisdiction: Two-letter jurisdiction code

        Returns:
            List of NewsStory objects
        """
        stories = []

        for result in results:
            try:
                title = result.get('title', '')
                url = self.clean_url(result.get('url', ''))
                snippet = result.get('snippet', '')
                source = result.get('source', '')

                # Try to extract date from multiple sources
                date_obj = self.extract_date_from_text(snippet)
                if not date_obj:
                    date_obj = self.extract_date_from_text(title)

                # If no date found, skip this article - strict date enforcement
                if not date_obj:
                    continue

                # Verify the date is within our target week range
                story_date = date_obj.date()
                if not (self.start_date <= story_date <= self.end_date):
                    continue  # Skip articles outside the target week

                # Create story object
                story = NewsStory(
                    title=title,
                    url=url,
                    source=source,
                    date=date_obj,
                    summary=snippet,
                    jurisdiction=jurisdiction,
                    snippet=snippet
                )

                stories.append(story)

            except Exception as e:
                # Skip malformed results
                continue

        return stories

    def collect_stories_for_jurisdiction(self, jurisdiction: str,
                                          search_function) -> List[NewsStory]:
        """
        Collect stories for a specific jurisdiction.

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
                stories = self.parse_search_results(results, jurisdiction)
                all_stories.extend(stories)
            except Exception as e:
                # Continue with other queries if one fails
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
        Collect stories from all jurisdictions.

        Args:
            search_function: Function that performs web search

        Returns:
            List of all NewsStory objects
        """
        from .config import ALL_JURISDICTIONS

        all_stories = []

        for jur_code in ALL_JURISDICTIONS.keys():
            stories = self.collect_stories_for_jurisdiction(jur_code, search_function)
            all_stories.extend(stories)

        self.stories = all_stories
        return all_stories
