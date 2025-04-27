import logging
import asyncio
from typing import Dict, Any, Optional
import trafilatura

logger = logging.getLogger(__name__)

class WebContentScraper:
    """
    Handles extracting text content from web pages using trafilatura
    """
    
    async def extract_text_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extracts the main text content from a webpage
        
        Args:
            url: The URL to extract content from
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        logger.debug(f"Extracting content from URL: {url}")
        
        try:
            # Run in a separate thread to not block the event loop
            loop = asyncio.get_event_loop()
            
            # Fetch the URL and extract content
            downloaded = await loop.run_in_executor(None, lambda: trafilatura.fetch_url(url))
            
            if not downloaded:
                logger.warning(f"Failed to download content from {url}")
                return {
                    "url": url,
                    "error": "Failed to download content",
                    "content": "",
                    "source": "web_scraper"
                }
            
            # Extract text content
            text = await loop.run_in_executor(None, lambda: trafilatura.extract(downloaded))
            
            # Extract metadata if possible
            metadata = await loop.run_in_executor(None, lambda: trafilatura.extract_metadata(downloaded))
            
            result = {
                "url": url,
                "content": text if text else "",
                "source": "web_scraper"
            }
            
            # Add metadata if available
            if metadata:
                for key in ["title", "author", "date", "description", "sitename"]:
                    if key in metadata and metadata[key]:
                        result[key] = metadata[key]
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return {
                "url": url,
                "error": str(e),
                "content": "",
                "source": "web_scraper"
            }
    
    async def process_urls(self, urls: list, max_urls: int = 5) -> Dict[str, Any]:
        """
        Process multiple URLs and extract their content
        
        Args:
            urls: List of URLs to process
            max_urls: Maximum number of URLs to process
            
        Returns:
            Dictionary with URL as key and extracted content as value
        """
        results = {}
        
        # Limit the number of URLs to process
        for url in urls[:max_urls]:
            result = await self.extract_text_from_url(url)
            results[url] = result
        
        return {
            "web_content": results,
            "source": "web_scraper"
        }