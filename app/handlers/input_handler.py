"""
OSINT Microagent - Input Handler
"""
import re
import ipaddress
from enum import Enum
from typing import Tuple, Dict, Any

import validators
from email_validator import validate_email, EmailNotValidError

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
        # Normalize query
        query = query.strip()
        
        if not query:
            return False, InputType.UNKNOWN, {}
        
        # Check if it's an email
        if "@" in query and "." in query:
            try:
                valid = validate_email(query)
                return True, InputType.EMAIL, {"email": valid.normalized, "domain": valid.domain}
            except EmailNotValidError:
                pass  # Not an email, continue checking other types
        
        # Check if it's an IP address
        try:
            ip = ipaddress.ip_address(query)
            return True, InputType.IP, {"ip": str(ip), "ip_version": ip.version}
        except ValueError:
            pass  # Not an IP, continue checking other types
        
        # Check if it's a domain
        if validators.domain(query):
            return True, InputType.DOMAIN, {"domain": query}
        
        # Check if it's a phone number (simple validation)
        phone_pattern = r"^\+?[0-9]{8,15}$"
        if re.match(phone_pattern, query.replace(" ", "").replace("-", "")):
            cleaned_phone = re.sub(r"[^\d+]", "", query)
            return True, InputType.PHONE, {"phone": cleaned_phone}
        
        # Check if it's a username (simple validation)
        username_pattern = r"^[\w\.-]{3,30}$"
        if re.match(username_pattern, query) and "." not in query:
            return True, InputType.USERNAME, {"username": query}
        
        # If it has spaces, assume it's a name
        if " " in query and all(x.isalpha() or x.isspace() for x in query):
            return True, InputType.NAME, {"name": query}
        
        # Default to treating it as a search query
        return True, InputType.UNKNOWN, {"search_query": query}
    
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
            return {}
        
        result = {
            "raw_query": query,
            "query_type": input_type.value,
            **parsed_data
        }
        
        return result
    
    @staticmethod
    def _get_sources_for_type(input_type: InputType) -> Dict[str, bool]:
        """
        Determines which data sources should be used based on input type
        
        Args:
            input_type: The type of the input
            
        Returns:
            Dictionary with source names as keys and boolean indicators as values
        """
        # Default sources (all disabled)
        sources = {
            "whois": False,
            "duckduckgo": False,
            "bing": False,
            "social_search": False,
            "ipinfo": False,
            "hunter": False,
            "haveibeenpwned": False
        }
        
        # Enable sources based on input type
        if input_type == InputType.EMAIL:
            sources.update({
                "duckduckgo": True,
                "bing": True,
                "hunter": True,
                "haveibeenpwned": True
            })
        elif input_type == InputType.DOMAIN:
            sources.update({
                "whois": True,
                "duckduckgo": True,
                "bing": True,
                "hunter": True
            })
        elif input_type == InputType.IP:
            sources.update({
                "whois": True,
                "ipinfo": True
            })
        elif input_type == InputType.USERNAME:
            sources.update({
                "duckduckgo": True,
                "bing": True,
                "social_search": True,
                "haveibeenpwned": True
            })
        elif input_type == InputType.NAME:
            sources.update({
                "duckduckgo": True,
                "bing": True,
                "social_search": True
            })
        elif input_type == InputType.PHONE:
            sources.update({
                "duckduckgo": True,
                "bing": True
            })
        else:  # UNKNOWN
            sources.update({
                "duckduckgo": True,
                "bing": True
            })
        
        return sources