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
        # Enhanced attributes
        self.credibility_score = 0.0
        self.why_it_matters = ""
        self.article_content = ""
        self.is_url_validated = False

    def __repr__(self):
        return f"NewsStory(title={self.title[:50]}, jurisdiction={self.jurisdiction})"


class NewsCollector:
    """Collects legal news stories from web searches with enhanced validation and content fetching."""

    def __init__(self, start_date, end_date, enable_validation=True, enable_content_fetch=True):
        self.start_date = start_date
        self.end_date = end_date
        self.stories = []
        self.enable_validation = enable_validation
        self.enable_content_fetch = enable_content_fetch

        # Initialize enhanced modules if enabled
        self.quality_scorer = None
        self.url_validator = None
        self.content_fetcher = None

        if enable_validation or enable_content_fetch:
            try:
                from .source_quality import SourceQualityScorer
                self.quality_scorer = SourceQualityScorer()

                if enable_validation:
                    from .content_fetcher import URLValidator
                    self.url_validator = URLValidator()

                if enable_content_fetch:
                    from .content_fetcher import ContentFetcher
                    self.content_fetcher = ContentFetcher()

            except ImportError as e:
                # Fallback if enhanced modules not available
                print(f"  Note: Enhanced features not available ({e}). Using basic collection.")
                self.enable_validation = False
                self.enable_content_fetch = False

    def build_search_queries(self, jurisdiction: str) -> List[str]:
        """
        Build search queries for a jurisdiction.

        Args:
            jurisdiction: Two-letter jurisdiction code

        Returns:
            List of search query strings
        """
        from .config import ALL_JURISDICTIONS

        jur_name = ALL_JURISDICTIONS[jurisdiction]['name']
        year = self.end_date.year

        # Core technology law topics
        topics = [
            'data privacy regulation',
            'cybersecurity law',
            'artificial intelligence regulation',
            'technology law',
            'digital regulation',
            'fintech regulation',
            'consumer protection digital'
        ]

        queries = []
        for topic in topics:
            # Build date-constrained queries
            queries.append(
                f'{jur_name} {topic} {year} law policy regulation'
            )

        return queries

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
        Parse search results into NewsStory objects with enhanced validation and content fetching.

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

                # Validate URL if enabled
                if self.enable_validation and self.url_validator:
                    is_valid, final_url, error = self.url_validator.validate_url(url)
                    if not is_valid:
                        # Skip invalid URLs
                        continue
                    url = final_url  # Use final URL after redirects

                # Check source quality
                if self.quality_scorer:
                    # Reject low-quality sources
                    if not self.quality_scorer.is_acceptable_source(url):
                        continue

                # Try to extract date
                date_obj = self.extract_date_from_text(snippet)
                if not date_obj:
                    date_obj = self.extract_date_from_text(title)
                if not date_obj:
                    # Default to end of week if we can't find a date
                    date_obj = datetime.combine(self.end_date, datetime.min.time())

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

                story.is_url_validated = self.enable_validation

                # Calculate source credibility
                if self.quality_scorer:
                    story.credibility_score = self.quality_scorer.calculate_source_credibility(
                        url, source, jurisdiction
                    )

                # Fetch full article content if enabled
                if self.enable_content_fetch and self.content_fetcher:
                    article = self.content_fetcher.fetch_article(url)
                    if article and article.get('content'):
                        story.article_content = article['content']
                        # Update with better extracted data if available
                        if article.get('title') and len(article['title']) > len(title):
                            story.title = article['title']
                        if article.get('date'):
                            story.date = article['date']

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
