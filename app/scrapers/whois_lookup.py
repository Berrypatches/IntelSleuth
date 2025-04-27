import logging
import asyncio
from typing import Dict, Any, Optional
import socket

# Try different whois packages
try:
    import python_whois as whois
    has_whois = True
except ImportError:
    try:
        import whois
        has_whois = True
    except ImportError:
        has_whois = False
        logging.warning("python-whois package not available, using limited WHOIS functionality")

logger = logging.getLogger(__name__)

class WhoisLookup:
    """
    Handles WHOIS lookups for domains and IP addresses
    """
    
    @staticmethod
    async def lookup_domain(domain: str) -> Dict[str, Any]:
        """
        Performs a WHOIS lookup for a domain
        
        Args:
            domain: The domain to lookup
            
        Returns:
            Dictionary containing WHOIS information
        """
        logger.debug(f"Performing WHOIS lookup for domain: {domain}")
        
        # Initialize with basic information
        result = {
            "domain": domain,
            "source": "whois",
            "note": "Basic information only (limited WHOIS access)"
        }
        
        # Only attempt to use whois if the module is available
        if has_whois:
            try:
                # Run whois lookup in a separate thread to not block the event loop
                loop = asyncio.get_event_loop()
                
                # Call whois.whois
                w = await loop.run_in_executor(None, lambda: whois.whois(domain))
                
                # Process the whois response if successful
                if w:
                    # Process common whois fields
                    for field in ["domain_name", "registrar", "whois_server", "creation_date", 
                              "updated_date", "expiration_date", "name_servers", 
                              "status", "emails", "dnssec"]:
                        if hasattr(w, field) and getattr(w, field):
                            value = getattr(w, field)
                            
                            # Convert datetime objects to strings
                            if isinstance(value, (list, tuple)):
                                str_values = []
                                for item in value:
                                    if hasattr(item, "strftime"):
                                        str_values.append(item.strftime("%Y-%m-%d %H:%M:%S"))
                                    else:
                                        str_values.append(str(item))
                                result[field] = str_values
                            elif hasattr(value, "strftime"):
                                result[field] = value.strftime("%Y-%m-%d %H:%M:%S")
                            else:
                                result[field] = str(value)
            except Exception as e:
                logger.warning(f"WHOIS lookup error: {e}")
        else:
            logger.warning("WHOIS lookup skipped as python-whois is not available")
            
        return result
    
    @staticmethod
    async def lookup_ip(ip: str) -> Dict[str, Any]:
        """
        Performs a basic lookup for an IP address (not full WHOIS)
        
        Args:
            ip: The IP address to lookup
            
        Returns:
            Dictionary containing basic IP information
        """
        logger.debug(f"Performing lookup for IP: {ip}")
        
        try:
            # Try to get hostname for the IP
            loop = asyncio.get_event_loop()
            hostname = await loop.run_in_executor(None, lambda: socket.getfqdn(ip))
            
            result = {
                "ip": ip,
                "hostname": hostname if hostname != ip else "No hostname found",
                "source": "whois"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in IP lookup for {ip}: {e}")
            return {"error": str(e), "source": "whois"}
    
    async def perform_lookup(self, query_data: Dict[str, Any], sources: Dict[str, bool]) -> Dict[str, Any]:
        """
        Performs WHOIS lookup based on query data
        
        Args:
            query_data: Parsed query data from InputHandler
            sources: Dictionary of source names and boolean indicators
            
        Returns:
            Dictionary with WHOIS information
        """
        if not sources.get("whois", False):
            return {}
        
        if "domain" in query_data:
            result = await self.lookup_domain(query_data["domain"])
            return {"whois": result}
        
        elif "ip" in query_data:
            result = await self.lookup_ip(query_data["ip"])
            return {"whois": result}
        
        return {}
