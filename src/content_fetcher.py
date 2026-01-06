"""Content fetching and URL validation for digest stories."""
import re
import requests
from typing import Tuple, Optional, Dict
from urllib.parse import urlparse, urljoin
from datetime import datetime


class URLValidator:
    """Validates URLs before including in digest."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def validate_url(self, url: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate URL accessibility and quality.

        Args:
            url: URL to validate

        Returns:
            Tuple of (is_valid, final_url, error_message)
        """
        try:
            # Check URL format
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False, None, "Invalid URL format"

            # Perform HEAD request to check accessibility
            response = self.session.head(
                url,
                timeout=self.timeout,
                allow_redirects=True
            )

            # Get final URL after redirects
            final_url = response.url

            # Check status code
            if response.status_code == 404:
                return False, None, "Page not found (404)"
            elif response.status_code == 403:
                return False, None, "Access forbidden (403)"
            elif response.status_code >= 400:
                return False, None, f"HTTP error {response.status_code}"

            # Check for paywalls (common headers)
            if self._is_paywalled(response):
                # Try to access anyway, might have free preview
                try:
                    full_response = self.session.get(final_url, timeout=self.timeout)
                    if self._is_paywalled_content(full_response.text):
                        return False, None, "Paywalled content"
                except:
                    return False, None, "Paywalled content"

            # Check content type
            content_type = response.headers.get('Content-Type', '').lower()
            if not any(t in content_type for t in ['text/html', 'text/plain', 'application/xhtml']):
                return False, None, f"Unsupported content type: {content_type}"

            return True, final_url, None

        except requests.exceptions.Timeout:
            return False, None, "Request timeout"
        except requests.exceptions.ConnectionError:
            return False, None, "Connection error"
        except requests.exceptions.TooManyRedirects:
            return False, None, "Too many redirects"
        except requests.exceptions.RequestException as e:
            return False, None, f"Request error: {str(e)}"
        except Exception as e:
            return False, None, f"Validation error: {str(e)}"

    def _is_paywalled(self, response: requests.Response) -> bool:
        """Check if response indicates paywall."""
        # Check headers for paywall indicators
        headers_str = str(response.headers).lower()
        paywall_indicators = [
            'x-paywall', 'subscription', 'subscriber-only',
            'premium-content', 'metered'
        ]
        return any(indicator in headers_str for indicator in paywall_indicators)

    def _is_paywalled_content(self, html: str) -> bool:
        """Check if HTML content indicates paywall."""
        html_lower = html.lower()
        paywall_patterns = [
            'subscribe to continue',
            'subscribers only',
            'subscription required',
            'premium article',
            'paywall',
            'this article is for subscribers'
        ]
        return any(pattern in html_lower for pattern in paywall_patterns)

    def batch_validate(self, urls: list) -> Dict[str, Tuple[bool, Optional[str], Optional[str]]]:
        """
        Validate multiple URLs.

        Args:
            urls: List of URLs to validate

        Returns:
            Dict mapping URL to validation result
        """
        results = {}
        for url in urls:
            results[url] = self.validate_url(url)
        return results


class ContentFetcher:
    """Fetches and extracts article content."""

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_article(self, url: str) -> Optional[Dict]:
        """
        Fetch article content.

        Args:
            url: Article URL

        Returns:
            Dict with article details or None if failed
        """
        try:
            # Try using trafilatura first (best for news extraction)
            try:
                import trafilatura

                downloaded = trafilatura.fetch_url(url)
                if downloaded:
                    # Extract with metadata
                    metadata = trafilatura.extract_metadata(downloaded)
                    text = trafilatura.extract(
                        downloaded,
                        include_comments=False,
                        include_tables=False,
                        no_fallback=False
                    )

                    if text and len(text) > 100:
                        return {
                            'title': metadata.title if metadata and metadata.title else '',
                            'content': text,
                            'author': metadata.author if metadata and metadata.author else '',
                            'date': metadata.date if metadata and metadata.date else None,
                            'url': url,
                            'method': 'trafilatura'
                        }
            except ImportError:
                pass  # Trafilatura not installed
            except Exception:
                pass  # Fall through to other methods

            # Fallback: Try newspaper3k
            try:
                from newspaper import Article

                article = Article(url)
                article.download()
                article.parse()

                if article.text and len(article.text) > 100:
                    return {
                        'title': article.title or '',
                        'content': article.text,
                        'author': ', '.join(article.authors) if article.authors else '',
                        'date': article.publish_date,
                        'url': url,
                        'method': 'newspaper'
                    }
            except ImportError:
                pass
            except Exception:
                pass

            # Last resort: Basic extraction with BeautifulSoup
            try:
                from bs4 import BeautifulSoup

                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "aside"]):
                    script.decompose()

                # Get title
                title = soup.find('title')
                title_text = title.get_text().strip() if title else ''

                # Try to find article content
                article_content = None

                # Look for common article containers
                for selector in ['article', 'main', '.article-content', '.post-content', '.entry-content']:
                    article_content = soup.find(selector)
                    if article_content:
                        break

                # If no article container, use body
                if not article_content:
                    article_content = soup.find('body')

                if article_content:
                    # Get text
                    text = article_content.get_text(separator='\n', strip=True)

                    # Clean up whitespace
                    text = re.sub(r'\n\s*\n', '\n\n', text)
                    text = re.sub(r' +', ' ', text)

                    if len(text) > 100:
                        return {
                            'title': title_text,
                            'content': text[:5000],  # Limit to 5000 chars
                            'author': '',
                            'date': None,
                            'url': url,
                            'method': 'beautifulsoup'
                        }

            except ImportError:
                pass
            except Exception:
                pass

            return None

        except Exception as e:
            return None

    def fetch_with_fallback(self, url: str, snippet: str = "") -> Dict:
        """
        Fetch article content with fallback to snippet.

        Args:
            url: Article URL
            snippet: Fallback snippet if fetch fails

        Returns:
            Dict with content
        """
        article = self.fetch_article(url)

        if article and article.get('content'):
            return article

        # Fallback to snippet
        return {
            'title': '',
            'content': snippet,
            'author': '',
            'date': None,
            'url': url,
            'method': 'snippet_fallback'
        }

    def extract_key_details(self, content: str) -> Dict:
        """
        Extract key details from article content.

        Args:
            content: Article text

        Returns:
            Dict with extracted details
        """
        details = {
            'has_dates': False,
            'has_organizations': False,
            'has_legal_terms': False,
            'word_count': 0
        }

        if not content:
            return details

        details['word_count'] = len(content.split())

        # Check for dates
        date_pattern = r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}'
        details['has_dates'] = bool(re.search(date_pattern, content, re.IGNORECASE))

        # Check for organizations (capitalized words)
        org_pattern = r'\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\b'
        orgs = re.findall(org_pattern, content)
        details['has_organizations'] = len(orgs) > 5

        # Check for legal terms
        legal_terms = [
            'regulation', 'law', 'act', 'legislation', 'statute',
            'compliance', 'enforcement', 'court', 'ruling', 'judgment'
        ]
        details['has_legal_terms'] = any(term in content.lower() for term in legal_terms)

        return details
