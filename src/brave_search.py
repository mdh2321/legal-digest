"""Brave Search API client for legal news collection."""
import os
import time
from pathlib import Path
from typing import List, Dict, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class BraveSearchClient:
    """Client for the Brave Search API."""

    API_URL = "https://api.search.brave.com/res/v1/web/search"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Brave Search client.

        Args:
            api_key: Brave Search API key. If not provided, loads from
                     BRAVE_SEARCH_API_KEY env var or brave_api_key.txt file.
        """
        self.api_key = api_key or self._load_api_key()
        self.enabled = bool(self.api_key) and REQUESTS_AVAILABLE
        self._last_request_time = 0.0

        if not REQUESTS_AVAILABLE:
            print("  [BraveSearch] requests package not installed. Run: pip install requests")
        elif not self.api_key:
            print("  [BraveSearch] No API key found. Set BRAVE_SEARCH_API_KEY or create brave_api_key.txt")

    def _load_api_key(self) -> Optional[str]:
        """Load API key from environment or file."""
        key = os.environ.get('BRAVE_SEARCH_API_KEY')
        if key:
            return key

        project_root = Path(__file__).parent.parent
        key_file = project_root / 'brave_api_key.txt'
        if key_file.exists():
            key = key_file.read_text().strip()
            if key and not key.startswith('#'):
                return key

        return None

    def _rate_limit(self):
        """Enforce 1 request/second rate limit (Brave free tier)."""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        self._last_request_time = time.time()

    def search(self, query: str, freshness: str = "pw", count: int = 20) -> List[Dict]:
        """
        Execute a web search via Brave Search API.

        Args:
            query: Search query string
            freshness: Time filter - "pd" (past day), "pw" (past week),
                      "pm" (past month), "py" (past year)
            count: Number of results to return (max 20)

        Returns:
            List of result dicts with keys: title, url, snippet, source
        """
        if not self.enabled:
            return []

        self._rate_limit()

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
        }
        params = {
            "q": query,
            "count": min(count, 20),
            "freshness": freshness,
        }

        max_retries = 2
        for attempt in range(max_retries):
            try:
                resp = requests.get(self.API_URL, headers=headers, params=params, timeout=15)

                if resp.status_code == 200:
                    return self._parse_response(resp.json())

                if resp.status_code in (429, 500, 502, 503) and attempt < max_retries - 1:
                    print(f"  [BraveSearch] HTTP {resp.status_code}, retrying...")
                    time.sleep(2)
                    continue

                # Non-retryable error
                print(f"  [BraveSearch] HTTP {resp.status_code} for query: {query[:60]}")
                return []

            except requests.RequestException:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return []

        return []

    def _parse_response(self, data: dict) -> List[Dict]:
        """Parse Brave API response into standard result format."""
        results = []
        web_results = data.get("web", {}).get("results", [])

        for item in web_results:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("description", ""),
                "source": self._extract_source(item.get("url", "")),
            })

        return results

    @staticmethod
    def _extract_source(url: str) -> str:
        """Extract a readable source name from URL."""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            # Remove www. prefix
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return url
