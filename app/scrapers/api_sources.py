import logging
import httpx
import asyncio
from typing import Dict, List, Any, Optional
import json

from app.config import settings

logger = logging.getLogger(__name__)

class APISources:
    """
    Handles fetching data from various API sources like IPinfo, Hunter.io, and HaveIBeenPwned
    """
    
    def __init__(self):
        self.ipinfo_api_key = settings.IPINFO_API_KEY
        self.hunter_api_key = settings.HUNTER_API_KEY
        self.hibp_api_key = settings.HIBP_API_KEY
        self.timeout = settings.TIMEOUT
    
    async def fetch_ipinfo(self, ip: str) -> Dict[str, Any]:
        """
        Fetches IP information from IPinfo.io
        
        Args:
            ip: The IP address to lookup
            
        Returns:
            Dictionary containing IP information
        """
        if not self.ipinfo_api_key:
            logger.warning("IPinfo API key not set")
            return {"error": "API key not configured"}
        
        url = f"https://ipinfo.io/{ip}?token={self.ipinfo_api_key}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Add source identifier
                data["source"] = "ipinfo"
                
                return data
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching IP info: {e}")
            return {"error": f"HTTP error: {e.response.status_code}"}
        except Exception as e:
            logger.error(f"Error fetching IP info: {e}")
            return {"error": str(e)}
    
    async def fetch_hunter_email_info(self, domain_or_email: str) -> Dict[str, Any]:
        """
        Fetches email information from Hunter.io
        
        Args:
            domain_or_email: The domain or email to lookup
            
        Returns:
            Dictionary containing email information
        """
        if not self.hunter_api_key:
            logger.warning("Hunter.io API key not set")
            return {"error": "API key not configured"}
        
        # Determine if input is domain or email
        is_email = '@' in domain_or_email
        
        if is_email:
            url = f"https://api.hunter.io/v2/email-verifier?email={domain_or_email}&api_key={self.hunter_api_key}"
        else:
            url = f"https://api.hunter.io/v2/domain-search?domain={domain_or_email}&api_key={self.hunter_api_key}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Add source identifier
                result = data.get("data", {})
                result["source"] = "hunter"
                
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching Hunter.io data: {e}")
            return {"error": f"HTTP error: {e.response.status_code}"}
        except Exception as e:
            logger.error(f"Error fetching Hunter.io data: {e}")
            return {"error": str(e)}
    
    async def fetch_haveibeenpwned(self, email_or_username: str) -> List[Dict[str, Any]]:
        """
        Fetches breach information from HaveIBeenPwned
        
        Args:
            email_or_username: The email or username to lookup
            
        Returns:
            List of dictionaries containing breach information
        """
        if not self.hibp_api_key:
            logger.warning("HaveIBeenPwned API key not set")
            return [{"error": "API key not configured"}]
        
        # Determine if input is email
        is_email = '@' in email_or_username
        
        if is_email:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email_or_username}"
        else:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email_or_username}?truncateResponse=false"
        
        headers = {
            "hibp-api-key": self.hibp_api_key,
            "User-Agent": "OSINT-Microagent"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 404:
                    # No breaches found
                    return []
                
                response.raise_for_status()
                data = response.json()
                
                # Add source identifier to each breach
                for breach in data:
                    breach["source"] = "haveibeenpwned"
                
                return data
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching HaveIBeenPwned data: {e}")
            if e.response.status_code == 404:
                # No breaches found is not an error
                return []
            return [{"error": f"HTTP error: {e.response.status_code}"}]
        except Exception as e:
            logger.error(f"Error fetching HaveIBeenPwned data: {e}")
            return [{"error": str(e)}]
    
    async def fetch_all(self, query_data: Dict[str, Any], sources: Dict[str, bool]) -> Dict[str, Any]:
        """
        Fetches data from all enabled API sources
        
        Args:
            query_data: Parsed query data from InputHandler
            sources: Dictionary of source names and boolean indicators
            
        Returns:
            Dictionary with source names as keys and API results as values
        """
        tasks = []
        results = {}
        
        if sources.get("ipinfo", False) and "ip" in query_data:
            tasks.append(self.fetch_ipinfo(query_data["ip"]))
            sources_list = ["ipinfo"]
        
        elif sources.get("hunter", False) and ("domain" in query_data or "email" in query_data):
            query = query_data.get("domain", query_data.get("email", ""))
            tasks.append(self.fetch_hunter_email_info(query))
            sources_list = ["hunter"]
        
        elif sources.get("haveibeenpwned", False) and ("email" in query_data or "username" in query_data):
            query = query_data.get("email", query_data.get("username", ""))
            tasks.append(self.fetch_haveibeenpwned(query))
            sources_list = ["haveibeenpwned"]
        
        if tasks:
            api_results = await asyncio.gather(*tasks)
            
            # Assign results to corresponding sources
            for i, source in enumerate(sources_list):
                results[source] = api_results[i]
        
        return results
