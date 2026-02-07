"""
HTML Fetcher Module - Robust web scraping utility

A production-ready HTML fetching utility with error handling, rate limiting,
and robots.txt compliance.
"""

import requests
import time
import random
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from typing import Dict, Optional, Any
from datetime import datetime


class HTMLFetcher:
    """Robust HTML fetcher with rate limiting and error handling."""
    
    # Rotate user agents to avoid bot detection
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    def __init__(self, 
                 min_delay: float = 1.0, 
                 max_delay: float = 3.0,
                 timeout: int = 10,
                 respect_robots: bool = True):
        """
        Initialize the HTML Fetcher.
        
        Args:
            min_delay: Minimum delay between requests (seconds)
            max_delay: Maximum delay between requests (seconds)
            timeout: Request timeout in seconds
            respect_robots: Whether to respect robots.txt
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.timeout = timeout
        self.respect_robots = respect_robots
        self.last_request_time = {}
        self.robots_cache = {}
        
    def _get_random_user_agent(self) -> str:
        """Get a random user agent string."""
        return random.choice(self.USER_AGENTS)
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _can_fetch(self, url: str, user_agent: str) -> bool:
        """
        Check if URL can be fetched according to robots.txt.
        
        Args:
            url: URL to check
            user_agent: User agent string
            
        Returns:
            True if allowed to fetch, False otherwise
        """
        if not self.respect_robots:
            return True
            
        domain = self._get_domain(url)
        
        # Check cache
        if domain not in self.robots_cache:
            rp = RobotFileParser()
            robots_url = urljoin(domain, '/robots.txt')
            try:
                rp.set_url(robots_url)
                rp.read()
                self.robots_cache[domain] = rp
            except Exception:
                # If we can't read robots.txt, assume allowed
                self.robots_cache[domain] = None
        
        robot_parser = self.robots_cache[domain]
        if robot_parser is None:
            return True
            
        return robot_parser.can_fetch(user_agent, url)
    
    def _apply_rate_limit(self, domain: str):
        """
        Apply rate limiting for domain.
        
        Args:
            domain: Domain to rate limit
        """
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            delay = random.uniform(self.min_delay, self.max_delay)
            
            if elapsed < delay:
                time.sleep(delay - elapsed)
        
        self.last_request_time[domain] = time.time()
    
    def fetch_html(self, url: str, 
                   headers: Optional[Dict[str, str]] = None,
                   cookies: Optional[Dict[str, str]] = None,
                   allow_redirects: bool = True,
                   max_retries: int = 3) -> Dict[str, Any]:
        """
        Fetch HTML content from a URL with robust error handling.
        
        Args:
            url: URL to fetch
            headers: Optional custom headers
            cookies: Optional cookies
            allow_redirects: Whether to follow redirects
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary containing:
                - url: Final URL (after redirects)
                - status_code: HTTP status code
                - html: HTML content (or None on error)
                - headers: Response headers
                - fetch_time: Time taken to fetch (seconds)
                - error: Error message (if any)
                - redirected: Whether the request was redirected
        """
        start_time = time.time()
        domain = self._get_domain(url)
        user_agent = self._get_random_user_agent()
        
        # Build headers
        request_headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        if headers:
            request_headers.update(headers)
        
        # Check robots.txt
        if not self._can_fetch(url, user_agent):
            return {
                'url': url,
                'status_code': None,
                'html': None,
                'headers': {},
                'fetch_time': time.time() - start_time,
                'error': 'Blocked by robots.txt',
                'redirected': False
            }
        
        # Apply rate limiting
        self._apply_rate_limit(domain)
        
        # Attempt fetch with retries
        last_error = None
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url,
                    headers=request_headers,
                    cookies=cookies,
                    timeout=self.timeout,
                    allow_redirects=allow_redirects
                )
                
                fetch_time = time.time() - start_time
                
                # Success - return result
                return {
                    'url': response.url,
                    'status_code': response.status_code,
                    'html': response.text if response.status_code == 200 else None,
                    'headers': dict(response.headers),
                    'fetch_time': fetch_time,
                    'error': None if response.status_code == 200 else f'HTTP {response.status_code}',
                    'redirected': response.url != url
                }
                
            except requests.exceptions.Timeout as e:
                last_error = f'Timeout after {self.timeout}s'
                if attempt < max_retries - 1:
                    time.sleep(1 * (attempt + 1))  # Exponential backoff
                    
            except requests.exceptions.ConnectionError as e:
                last_error = f'Connection error: {str(e)}'
                if attempt < max_retries - 1:
                    time.sleep(1 * (attempt + 1))
                    
            except requests.exceptions.TooManyRedirects as e:
                last_error = 'Too many redirects'
                break  # Don't retry
                
            except requests.exceptions.RequestException as e:
                last_error = f'Request error: {str(e)}'
                if attempt < max_retries - 1:
                    time.sleep(1 * (attempt + 1))
        
        # All retries failed
        fetch_time = time.time() - start_time
        return {
            'url': url,
            'status_code': None,
            'html': None,
            'headers': {},
            'fetch_time': fetch_time,
            'error': last_error,
            'redirected': False
        }


# Convenience function for simple usage
def fetch_html(url: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to fetch HTML from a URL.
    
    Args:
        url: URL to fetch
        **kwargs: Additional arguments passed to HTMLFetcher
        
    Returns:
        Dictionary with fetch results
        
    Example:
        >>> result = fetch_html('https://example.com')
        >>> if result['error'] is None:
        ...     print(result['html'])
    """
    fetcher = HTMLFetcher()
    return fetcher.fetch_html(url, **kwargs)


if __name__ == "__main__":
    # Quick test
    print("Testing HTML Fetcher...")
    result = fetch_html('https://example.com')
    print(f"Status: {result['status_code']}")
    print(f"Fetch time: {result['fetch_time']:.2f}s")
    print(f"Error: {result['error']}")
    if result['html']:
        print(f"HTML length: {len(result['html'])} chars")
