"""
OSINT Microagent - WHOIS Lookup
"""
import logging
import socket
import whois
import subprocess
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class WhoisLookup:
    """
    Handles WHOIS lookups for domains and IP addresses
    """
    
    async def perform_lookup(self, query_data: Dict[str, Any], sources: Dict[str, bool]) -> Dict[str, Any]:
        """
        Performs a WHOIS lookup for the specified domain or IP
        
        Args:
            query_data: Parsed query data
            sources: Dictionary of enabled sources
            
        Returns:
            Dictionary with lookup results
        """
        if not sources.get("whois", False):
            return {}
        
        result = {}
        
        # Domain lookup
        if "domain" in query_data:
            domain_info = await self._lookup_domain(query_data["domain"])
            if domain_info:
                result["domain"] = domain_info
        
        # IP lookup
        if "ip" in query_data:
            ip_info = await self._lookup_ip(query_data["ip"])
            if ip_info:
                result["ip"] = ip_info
        
        return result
    
    async def _lookup_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Performs a WHOIS lookup for a domain name
        
        Args:
            domain: The domain name to lookup
            
        Returns:
            Dictionary with domain WHOIS information or None if lookup fails
        """
        try:
            # Try using python-whois library
            w = whois.whois(domain)
            
            # Extract relevant information
            result = {
                "domain_name": w.domain_name,
                "registrar": w.registrar,
                "creation_date": w.creation_date,
                "expiration_date": w.expiration_date,
                "updated_date": w.updated_date,
                "name_servers": w.name_servers,
                "status": w.status,
                "emails": w.emails,
                "dnssec": w.dnssec,
                "org": w.org
            }
            
            # Filter out None values
            result = {k: v for k, v in result.items() if v is not None}
            
            return result
        except Exception as primary_error:
            logger.warning(f"Primary WHOIS lookup for {domain} failed: {str(primary_error)}")
            
            # Fallback to command-line whois tool
            try:
                whois_output = subprocess.check_output(["whois", domain], 
                                                      universal_newlines=True,
                                                      stderr=subprocess.STDOUT,
                                                      timeout=10)
                
                # Parse the raw whois output
                result = self._parse_raw_whois(whois_output)
                return result
            except Exception as fallback_error:
                logger.error(f"Fallback WHOIS lookup for {domain} failed: {str(fallback_error)}")
                return {"error": "WHOIS lookup failed", "domain": domain}
    
    async def _lookup_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        """
        Performs a WHOIS lookup for an IP address
        
        Args:
            ip: The IP address to lookup
            
        Returns:
            Dictionary with IP WHOIS information or None if lookup fails
        """
        try:
            # Try getting hostname
            hostname = socket.getfqdn(ip)
            if hostname != ip:  # If not the same as the IP
                host_info = {"hostname": hostname}
            else:
                host_info = {}
            
            # Use command-line whois tool for IP (better than python-whois for IPs)
            try:
                whois_output = subprocess.check_output(["whois", ip], 
                                                      universal_newlines=True,
                                                      stderr=subprocess.STDOUT,
                                                      timeout=10)
                
                # Parse the raw whois output
                whois_info = self._parse_raw_whois(whois_output)
                
                # Combine results
                result = {**host_info, **whois_info}
                return result
            except Exception as fallback_error:
                logger.error(f"WHOIS lookup for IP {ip} failed: {str(fallback_error)}")
                if host_info:  # If we at least got hostname info
                    return host_info
                return {"error": "WHOIS lookup failed", "ip": ip}
        except Exception as e:
            logger.error(f"IP lookup for {ip} failed: {str(e)}")
            return {"error": "IP lookup failed", "ip": ip}
    
    def _parse_raw_whois(self, raw_output: str) -> Dict[str, Any]:
        """
        Parses raw WHOIS output into a structured format
        
        Args:
            raw_output: Raw WHOIS output text
            
        Returns:
            Dictionary with structured WHOIS information
        """
        result = {"raw_text": raw_output}
        
        # Extract common fields
        lines = raw_output.splitlines()
        
        # Known important fields
        field_mapping = {
            "domain name": "domain_name",
            "registrar": "registrar",
            "created": "creation_date",
            "creation date": "creation_date",
            "registrar registration expiration date": "expiration_date",
            "updated date": "updated_date",
            "name server": "name_servers",
            "status": "status",
            "registrant name": "registrant_name",
            "registrant organization": "registrant_organization",
            "registrant email": "registrant_email",
            "admin name": "admin_name",
            "admin email": "admin_email",
            "tech name": "tech_name",
            "tech email": "tech_email",
            "netname": "netname",
            "netrange": "netrange",
            "organization": "organization",
            "org": "organization",
            "cidr": "cidr",
            "country": "country"
        }
        
        extracted_data = {}
        name_servers = []
        
        for line in lines:
            line = line.strip()
            if not line or ":" not in line:
                continue
                
            parts = line.split(":", 1)
            key = parts[0].strip().lower()
            value = parts[1].strip()
            
            # Map the field if it's in our mapping
            if key in field_mapping:
                mapped_key = field_mapping[key]
                
                # Handle name servers separately to collect them into a list
                if mapped_key == "name_servers":
                    name_servers.append(value)
                    extracted_data[mapped_key] = name_servers
                else:
                    extracted_data[mapped_key] = value
        
        # Add extracted data to result
        result.update(extracted_data)
        
        return result