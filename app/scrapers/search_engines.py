"""
OSINT Microagent - Search Engines Scraper
"""
import logging
import re
from typing import List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup

from app.config import settings
from app.scrapers.web_content_scraper import WebContentScraper

logger = logging.getLogger(__name__)

class SearchEngineScraper:
    """
    Handles scraping of search engines like DuckDuckGo and Bing
    """
    
    def __init__(self):
        """
        Initialize the search engine scraper
        """
        self.headers = {
            "User-Agent": settings.USER_AGENT
        }
        self.web_scraper = WebContentScraper()
        self.max_results = settings.MAX_RESULTS_PER_SOURCE
    
    async def search_duckduckgo(self, query: str) -> List[Dict[str, Any]]:
        """
        Scrapes DuckDuckGo search results for the given query
        
        Args:
            query: The search query string
            
        Returns:
            List of dictionaries containing search results with url, title, and snippet
        """
        try:
            # Construct the DuckDuckGo search URL
            search_url = f"https://html.duckduckgo.com/html/?q={query}"
            
            # Send the request
            async with httpx.AsyncClient(headers=self.headers, timeout=settings.TIMEOUT) as client:
                response = await client.get(search_url)
                response.raise_for_status()
                
                # Parse the HTML
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Extract search results
                results = []
                result_elements = soup.select(".result")
                
                for element in result_elements[:self.max_results]:
                    # Extract result details
                    title_element = element.select_one(".result__title")
                    link_element = element.select_one(".result__url")
                    snippet_element = element.select_one(".result__snippet")
                    
                    if title_element and link_element:
                        # Extract title text
                        title = title_element.get_text(strip=True)
                        
                        # Extract URL
                        href = title_element.select_one("a")["href"]
                        # Clean the URL (DuckDuckGo URLs contain redirects)
                        url = self._extract_url_from_ddg_redirect(href)
                        
                        # Extract snippet
                        snippet = snippet_element.get_text(strip=True) if snippet_element else ""
                        
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "source": "DuckDuckGo"
                        })
                
                return results
                
        except Exception as e:
            logger.error(f"Error searching DuckDuckGo for '{query}': {str(e)}")
            return []
    
    async def search_bing(self, query: str) -> List[Dict[str, Any]]:
        """
        Scrapes Bing search results for the given query
        
        Args:
            query: The search query string
            
        Returns:
            List of dictionaries containing search results with url, title, and snippet
        """
        try:
            # Construct the Bing search URL
            search_url = f"https://www.bing.com/search?q={query}"
            
            # Send the request
            async with httpx.AsyncClient(headers=self.headers, timeout=settings.TIMEOUT) as client:
                response = await client.get(search_url)
                response.raise_for_status()
                
                # Parse the HTML
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Extract search results
                results = []
                result_elements = soup.select(".b_algo")
                
                for element in result_elements[:self.max_results]:
                    # Extract result details
                    title_element = element.select_one("h2")
                    link_element = element.select_one("h2 a")
                    snippet_element = element.select_one(".b_caption p")
                    
                    if title_element and link_element and "href" in link_element.attrs:
                        # Extract title text
                        title = title_element.get_text(strip=True)
                        
                        # Extract URL
                        url = link_element["href"]
                        
                        # Extract snippet
                        snippet = snippet_element.get_text(strip=True) if snippet_element else ""
                        
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "source": "Bing"
                        })
                
                return results
                
        except Exception as e:
            logger.error(f"Error searching Bing for '{query}': {str(e)}")
            return []
    
    async def fetch_page_content(self, url: str) -> Optional[str]:
        """
        Fetches the content of a page and extracts the main text
        
        Args:
            url: The URL to fetch
            
        Returns:
            Extracted text content or None if extraction fails
        """
        try:
            result = await self.web_scraper.extract_text_from_url(url)
            if result and "text" in result:
                return result["text"]
            return None
        except Exception as e:
            logger.error(f"Error fetching content from {url}: {str(e)}")
            return None
    
    async def search_all(self, query: str, sources: Dict[str, bool]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Searches across all enabled search engines
        
        Args:
            query: The search query string
            sources: Dictionary of source names and boolean indicators
            
        Returns:
            Dictionary with source names as keys and search results as values
        """
        results = {}
        
        # Search DuckDuckGo if enabled
        if sources.get("duckduckgo", False):
            ddg_results = await self.search_duckduckgo(query)
            if ddg_results:
                results["duckduckgo"] = ddg_results
        
        # Search Bing if enabled
        if sources.get("bing", False):
            bing_results = await self.search_bing(query)
            if bing_results:
                results["bing"] = bing_results
        
        return results
    
    def _extract_url_from_ddg_redirect(self, redirect_url: str) -> str:
        """
        Extracts the actual URL from a DuckDuckGo redirect URL
        
        Args:
            redirect_url: The DuckDuckGo redirect URL
            
        Returns:
            The extracted actual URL
        """
        # Pattern to match URLs in DuckDuckGo redirect
        pattern = r"uddg=([^&]+)"
        
        match = re.search(pattern, redirect_url)
        if match:
            # URL decode the matched URL
            import urllib.parse
            return urllib.parse.unquote(match.group(1))
        
        return redirect_url