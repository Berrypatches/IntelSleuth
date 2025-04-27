"""
OSINT Microagent - API Sources
"""
import logging
from typing import Dict, Any, List, Optional
import httpx
import json

from app.config import settings

logger = logging.getLogger(__name__)

class APISources:
    """
    Handles fetching data from various API sources like IPinfo, Hunter.io, and HaveIBeenPwned
    """
    
    def __init__(self):
        """
        Initialize the API sources
        """
        self.ipinfo_api_key = settings.IPINFO_API_KEY
        self.hunter_api_key = settings.HUNTER_API_KEY
        self.hibp_api_key = settings.HIBP_API_KEY
        self.headers = {
            "User-Agent": settings.USER_AGENT
        }
    
    async def fetch_ipinfo(self, ip: str) -> Dict[str, Any]:
        """
        Fetches IP information from IPinfo.io
        
        Args:
            ip: The IP address to lookup
            
        Returns:
            Dictionary containing IP information
        """
        if not self.ipinfo_api_key:
            logger.warning("IPinfo API key not set. Skipping IPinfo lookup.")
            return {"error": "IPinfo API key not set"}
        
        try:
            url = f"https://ipinfo.io/{ip}/json?token={self.ipinfo_api_key}"
            async with httpx.AsyncClient(headers=self.headers, timeout=settings.TIMEOUT) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Handle potential error responses
                if "error" in data:
                    return {"error": data.get("error", {}).get("title", "Unknown error")}
                
                return data
                
        except Exception as e:
            error_msg = f"Error fetching IPinfo for {ip}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    async def fetch_hunter_email_info(self, domain_or_email: str) -> Dict[str, Any]:
        """
        Fetches email information from Hunter.io
        
        Args:
            domain_or_email: The domain or email to lookup
            
        Returns:
            Dictionary containing email information
        """
        if not self.hunter_api_key:
            logger.warning("Hunter.io API key not set. Skipping Hunter.io lookup.")
            return {"error": "Hunter.io API key not set"}
        
        try:
            # Determine if input is a domain or email
            if "@" in domain_or_email:
                # Email lookup
                url = f"https://api.hunter.io/v2/email-verifier?email={domain_or_email}&api_key={self.hunter_api_key}"
            else:
                # Domain lookup
                url = f"https://api.hunter.io/v2/domain-search?domain={domain_or_email}&api_key={self.hunter_api_key}"
            
            async with httpx.AsyncClient(headers=self.headers, timeout=settings.TIMEOUT) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Handle potential error responses
                if "errors" in data:
                    errors = data.get("errors", [])
                    error_msg = errors[0].get("details") if errors else "Unknown error"
                    return {"error": error_msg}
                
                return data.get("data", {})
                
        except Exception as e:
            error_msg = f"Error fetching Hunter.io data for {domain_or_email}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    async def fetch_haveibeenpwned(self, email_or_username: str) -> List[Dict[str, Any]]:
        """
        Fetches breach information from HaveIBeenPwned
        
        Args:
            email_or_username: The email or username to lookup
            
        Returns:
            List of dictionaries containing breach information
        """
        if not self.hibp_api_key:
            logger.warning("HaveIBeenPwned API key not set. Skipping HaveIBeenPwned lookup.")
            return [{"error": "HaveIBeenPwned API key not set"}]
        
        try:
            # Determine if input is an email (contains @)
            lookup_url = "breachedaccount"
            
            # Construct the URL
            url = f"https://haveibeenpwned.com/api/v3/{lookup_url}/{email_or_username}"
            
            # Add specific headers for HIBP
            headers = {
                **self.headers,
                "hibp-api-key": self.hibp_api_key
            }
            
            async with httpx.AsyncClient(headers=headers, timeout=settings.TIMEOUT) as client:
                response = await client.get(url)
                
                # Check for specific status codes
                if response.status_code == 404:
                    # 404 means not found in any breaches
                    return []
                
                response.raise_for_status()
                
                # Parse the response
                data = response.json()
                return data
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # 404 means not found in any breaches, which is not an error
                return []
            error_msg = f"HTTP error fetching HaveIBeenPwned data for {email_or_username}: {str(e)}"
            logger.error(error_msg)
            return [{"error": error_msg}]
        except Exception as e:
            error_msg = f"Error fetching HaveIBeenPwned data for {email_or_username}: {str(e)}"
            logger.error(error_msg)
            return [{"error": error_msg}]
    
    async def fetch_all(self, query_data: Dict[str, Any], sources: Dict[str, bool]) -> Dict[str, Any]:
        """
        Fetches data from all enabled API sources
        
        Args:
            query_data: Parsed query data from InputHandler
            sources: Dictionary of source names and boolean indicators
            
        Returns:
            Dictionary with source names as keys and API results as values
        """
        results = {}
        
        # IP info lookup
        if sources.get("ipinfo", False) and "ip" in query_data:
            ip_info = await self.fetch_ipinfo(query_data["ip"])
            if ip_info and not (len(ip_info) == 1 and "error" in ip_info):
                results["ipinfo"] = ip_info
        
        # Hunter.io lookup
        if sources.get("hunter", False):
            # Determine what to look up
            if "domain" in query_data:
                hunter_data = await self.fetch_hunter_email_info(query_data["domain"])
                if hunter_data and not (len(hunter_data) == 1 and "error" in hunter_data):
                    results["hunter"] = hunter_data
            elif "email" in query_data:
                hunter_data = await self.fetch_hunter_email_info(query_data["email"])
                if hunter_data and not (len(hunter_data) == 1 and "error" in hunter_data):
                    results["hunter"] = hunter_data
        
        # HaveIBeenPwned lookup
        if sources.get("haveibeenpwned", False):
            # Determine what to look up
            if "email" in query_data:
                hibp_data = await self.fetch_haveibeenpwned(query_data["email"])
                if hibp_data and not (len(hibp_data) == 1 and "error" in hibp_data[0]):
                    results["haveibeenpwned"] = hibp_data
            elif "username" in query_data:
                hibp_data = await self.fetch_haveibeenpwned(query_data["username"])
                if hibp_data and not (len(hibp_data) == 1 and "error" in hibp_data[0]):
                    results["haveibeenpwned"] = hibp_data
        
        return results