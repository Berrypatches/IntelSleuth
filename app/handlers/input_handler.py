import re
import validators
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class InputType(str, Enum):
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    USERNAME = "username"
    DOMAIN = "domain"
    IP = "ip"
    UNKNOWN = "unknown"

class InputHandler:
    """
    Handles the processing and validation of user input queries
    """
    
    @staticmethod
    def validate_and_identify(query: str) -> Tuple[bool, InputType, Dict[str, Any]]:
        """
        Validates the input and identifies its type
        
        Args:
            query: The user input string
            
        Returns:
            Tuple containing:
            - Boolean indicating if input is valid
            - InputType enum identifying the type of input
            - Dictionary with parsed components of the input
        """
        if not query or not isinstance(query, str):
            return False, InputType.UNKNOWN, {}
        
        query = query.strip()
        
        # Check for email
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', query):
            logger.debug(f"Input identified as email: {query}")
            username, domain = query.split('@')
            return True, InputType.EMAIL, {
                "email": query,
                "username": username,
                "domain": domain
            }
        
        # Check for domain
        if validators.domain(query):
            logger.debug(f"Input identified as domain: {query}")
            return True, InputType.DOMAIN, {"domain": query}
        
        # Check for IP address
        if validators.ipv4(query) or validators.ipv6(query):
            logger.debug(f"Input identified as IP address: {query}")
            return True, InputType.IP, {"ip": query}
        
        # Check for phone number (basic check, can be improved)
        if re.match(r'^\+?[0-9\s\-\(\)]{7,20}$', query):
            # Normalize phone number
            normalized = re.sub(r'[^0-9+]', '', query)
            logger.debug(f"Input identified as phone number: {normalized}")
            return True, InputType.PHONE, {"phone": normalized}
        
        # Check for username (basic check)
        if re.match(r'^[a-zA-Z0-9_\.]{3,30}$', query):
            logger.debug(f"Input identified as username: {query}")
            return True, InputType.USERNAME, {"username": query}
        
        # If no specific format is detected, treat as a name or general search term
        if len(query.split()) >= 1:
            logger.debug(f"Input identified as name or search term: {query}")
            return True, InputType.NAME, {"name": query}
        
        return False, InputType.UNKNOWN, {}
    
    @staticmethod
    def parse_query(query: str) -> Dict[str, Any]:
        """
        Parses the query string into a structured format for the scrapers
        
        Args:
            query: The user input string
            
        Returns:
            Dictionary with structured query information
        """
        is_valid, input_type, parsed_data = InputHandler.validate_and_identify(query)
        
        if not is_valid:
            return {
                "valid": False,
                "query": query,
                "type": InputType.UNKNOWN,
                "data": {}
            }
        
        # Determine which sources to use based on input type
        sources_to_use = InputHandler._get_sources_for_type(input_type)
        
        return {
            "valid": True,
            "query": query,
            "type": input_type,
            "data": parsed_data,
            "sources": sources_to_use
        }
    
    @staticmethod
    def _get_sources_for_type(input_type: InputType) -> Dict[str, bool]:
        """
        Determines which data sources should be used based on input type
        
        Args:
            input_type: The type of the input
            
        Returns:
            Dictionary with source names as keys and boolean indicators as values
        """
        # Base configuration - enable all by default
        sources = {
            "duckduckgo": False,
            "bing": False,
            "whois": False,
            "ipinfo": False,
            "hunter": False,
            "haveibeenpwned": False
        }
        
        # Customize based on input type
        if input_type == InputType.NAME:
            sources.update({"duckduckgo": True, "bing": True})
        
        elif input_type == InputType.EMAIL:
            sources.update({
                "duckduckgo": True, 
                "hunter": True, 
                "haveibeenpwned": True
            })
        
        elif input_type == InputType.PHONE:
            sources.update({"duckduckgo": True, "bing": True})
        
        elif input_type == InputType.USERNAME:
            sources.update({
                "duckduckgo": True, 
                "bing": True, 
                "haveibeenpwned": True
            })
        
        elif input_type == InputType.DOMAIN:
            sources.update({
                "duckduckgo": True, 
                "whois": True, 
                "hunter": True
            })
        
        elif input_type == InputType.IP:
            sources.update({
                "whois": True, 
                "ipinfo": True
            })
        
        return sources
