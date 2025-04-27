import logging
import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from urllib.parse import quote
import trafilatura

from app.config import settings

logger = logging.getLogger(__name__)

class SearchEngineScraper:
    """
    Handles scraping of search engines like DuckDuckGo and Bing
    """
    
    def __init__(self):
        self.user_agent = settings.USER_AGENT
        self.timeout = settings.TIMEOUT
        self.max_results = settings.MAX_RESULTS_PER_SOURCE
    
    async def search_duckduckgo(self, query: str) -> List[Dict[str, Any]]:
        """
        Scrapes DuckDuckGo search results for the given query
        
        Args:
            query: The search query string
            
        Returns:
            List of dictionaries containing search results with url, title, and snippet
        """
        encoded_query = quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        logger.debug(f"Searching DuckDuckGo for: {query}")
        
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                results = []
                
                # DuckDuckGo results are in <div class="result">
                for result in soup.select(".result")[:self.max_results]:
                    title_elem = result.select_one(".result__title a")
                    snippet_elem = result.select_one(".result__snippet")
                    
                    if title_elem and snippet_elem:
                        title = title_elem.get_text(strip=True)
                        link = title_elem.get("href", "")
                        
                        # Clean the URL - DuckDuckGo uses redirects
                        if "/d.js?" in link:
                            link_parts = link.split("uddg=")
                            if len(link_parts) > 1:
                                link = link_parts[1].split("&")[0]
                        
                        snippet = snippet_elem.get_text(strip=True)
                        
                        results.append({
                            "title": title,
                            "url": link,
                            "snippet": snippet,
                            "source": "duckduckgo"
                        })
                
                logger.debug(f"Found {len(results)} results from DuckDuckGo")
                return results
                
        except httpx.RequestError as e:
            logger.error(f"Error searching DuckDuckGo: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in DuckDuckGo search: {e}")
            return []
    
    async def search_bing(self, query: str) -> List[Dict[str, Any]]:
        """
        Scrapes Bing search results for the given query
        
        Args:
            query: The search query string
            
        Returns:
            List of dictionaries containing search results with url, title, and snippet
        """
        encoded_query = quote(query)
        url = f"https://www.bing.com/search?q={encoded_query}"
        
        logger.debug(f"Searching Bing for: {query}")
        
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                results = []
                
                # Bing results are in <li class="b_algo">
                for result in soup.select(".b_algo")[:self.max_results]:
                    title_elem = result.select_one("h2 a")
                    snippet_elem = result.select_one(".b_caption p")
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link = title_elem.get("href", "")
                        snippet = ""
                        
                        if snippet_elem:
                            snippet = snippet_elem.get_text(strip=True)
                        
                        results.append({
                            "title": title,
                            "url": link,
                            "snippet": snippet,
                            "source": "bing"
                        })
                
                logger.debug(f"Found {len(results)} results from Bing")
                return results
                
        except httpx.RequestError as e:
            logger.error(f"Error searching Bing: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Bing search: {e}")
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
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers={"User-Agent": self.user_agent})
                response.raise_for_status()
                
                # Use trafilatura to extract main content
                text = trafilatura.extract(response.text)
                return text
                
        except Exception as e:
            logger.error(f"Error fetching page content from {url}: {e}")
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
        tasks = []
        results = {}
        
        if sources.get("duckduckgo", False):
            tasks.append(self.search_duckduckgo(query))
        
        if sources.get("bing", False):
            tasks.append(self.search_bing(query))
        
        if tasks:
            search_results = await asyncio.gather(*tasks)
            
            # Combine results from all sources
            index = 0
            if sources.get("duckduckgo", False):
                results["duckduckgo"] = search_results[index]
                index += 1
            
            if sources.get("bing", False):
                results["bing"] = search_results[index]
        
        return results
