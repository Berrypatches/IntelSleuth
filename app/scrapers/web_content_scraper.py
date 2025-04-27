"""
OSINT Microagent - Web Content Scraper
"""
import logging
from typing import Dict, Any, Optional
import httpx
import trafilatura
from bs4 import BeautifulSoup

from app.config import settings

logger = logging.getLogger(__name__)

class WebContentScraper:
    """
    Handles the scraping of web content from URLs
    """
    
    def __init__(self):
        """
        Initialize the web content scraper
        """
        self.headers = {
            "User-Agent": settings.USER_AGENT
        }
    
    async def extract_text_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extracts the text content from a URL
        
        Args:
            url: The URL to extract text from
            
        Returns:
            Dictionary containing extracted content
        """
        try:
            # Download content
            downloaded = await self.fetch_url(url)
            if not downloaded:
                return {"error": "Failed to download content", "url": url}
            
            # Extract text using trafilatura (high quality content extraction)
            text = trafilatura.extract(downloaded)
            
            # If trafilatura fails, fallback to BeautifulSoup
            if not text:
                soup = BeautifulSoup(downloaded, "html.parser")
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                
                # Extract text
                text = soup.get_text(separator=" ")
                
                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = "\\n".join(chunk for chunk in chunks if chunk)
            
            # Extract title
            title = self._extract_title(downloaded)
            
            return {
                "url": url,
                "title": title,
                "text": text
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from {url}: {str(e)}")
            return {
                "error": f"Error extracting text: {str(e)}",
                "url": url
            }
    
    async def fetch_url(self, url: str) -> Optional[str]:
        """
        Fetches the content of a URL
        
        Args:
            url: The URL to fetch
            
        Returns:
            HTML content as string or None if failed
        """
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=settings.TIMEOUT) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def _extract_title(self, html: str) -> Optional[str]:
        """
        Extracts the title from HTML content
        
        Args:
            html: HTML content
            
        Returns:
            Title string or None if not found
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            title_tag = soup.find("title")
            if title_tag:
                return title_tag.string.strip()
            return None
        except Exception:
            return None