import logging
import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)

class WebhookExporter:
    """
    Handles exporting results to webhooks
    """
    
    async def send_to_webhook(self, results: Dict[str, Any], webhook_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Sends the results to a webhook endpoint
        
        Args:
            results: The results to send
            webhook_url: The webhook URL to send to (optional, uses default if not provided)
            
        Returns:
            Dictionary with status and message
        """
        url = webhook_url or settings.DEFAULT_WEBHOOK_URL
        
        if not url:
            logger.warning("No webhook URL provided and no default configured")
            return {
                "success": False,
                "message": "No webhook URL provided and no default configured"
            }
        
        # Prepare payload
        payload = {
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                response.raise_for_status()
                
                logger.info(f"Successfully sent results to webhook: {url}")
                return {
                    "success": True,
                    "message": "Results successfully sent to webhook",
                    "status_code": response.status_code
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending to webhook: {e}")
            return {
                "success": False,
                "message": f"HTTP error: {e.response.status_code}",
                "status_code": e.response.status_code
            }
        except Exception as e:
            logger.error(f"Error sending to webhook: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def format_for_n8n(self, results: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        Formats the results specifically for n8n integration
        
        Args:
            results: The results to format
            query: The original query string
            
        Returns:
            Dictionary formatted for n8n
        """
        # Create a simplified structure that works well with n8n
        n8n_payload = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "summary": results.get("summary", "No summary available"),
            "categories": {}
        }
        
        # Add categories
        for category in ["emails", "phone_numbers", "social_links", "addresses", 
                         "business_info", "leaks", "domains", "ips"]:
            if category in results and results[category]:
                n8n_payload["categories"][category] = results[category]
        
        return n8n_payload
