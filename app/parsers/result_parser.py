"""
OSINT Microagent - Result Parser
"""
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ResultParser:
    """
    Parses, filters and categorizes the raw results from various sources
    """
    
    def extract_emails(self, text: str) -> List[str]:
        """
        Extracts email addresses from text
        
        Args:
            text: The text to extract emails from
            
        Returns:
            List of extracted email addresses
        """
        # Email pattern
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return list(set(re.findall(pattern, text)))
    
    def extract_phone_numbers(self, text: str) -> List[str]:
        """
        Extracts phone numbers from text
        
        Args:
            text: The text to extract phone numbers from
            
        Returns:
            List of extracted phone numbers
        """
        # Phone number patterns (international format, US format, etc.)
        patterns = [
            r'\+\d{1,3}\s?[\(\)\-\d\s]{8,}',  # International format: +1 123-456-7890
            r'\(\d{3}\)\s?\d{3}[-\s]?\d{4}',   # US format: (123) 456-7890
            r'\d{3}[-\s]?\d{3}[-\s]?\d{4}'     # US format without parentheses: 123-456-7890
        ]
        
        results = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            results.extend(matches)
        
        return list(set(results))
    
    def extract_social_links(self, text: str) -> List[str]:
        """
        Extracts social media links from text
        
        Args:
            text: The text to extract social links from
            
        Returns:
            List of extracted social media links
        """
        # Social media domains
        social_domains = [
            'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com',
            'github.com', 'pinterest.com', 'youtube.com', 'tiktok.com',
            'reddit.com', 'tumblr.com', 'snapchat.com', 'quora.com',
            'medium.com', 'flickr.com', 'vimeo.com', 'soundcloud.com'
        ]
        
        # URL pattern
        url_pattern = r'https?://[^\s<>"\'()]+(?<![\.\?!,])'
        urls = re.findall(url_pattern, text)
        
        # Filter for social media links
        social_links = []
        for url in urls:
            if any(domain in url.lower() for domain in social_domains):
                social_links.append(url)
        
        return list(set(social_links))
    
    def extract_addresses(self, text: str) -> List[str]:
        """
        Extracts physical addresses from text (simplified version)
        
        Args:
            text: The text to extract addresses from
            
        Returns:
            List of extracted address candidates
        """
        # This is a simplified approach that looks for address-like patterns
        # A full address parser would be much more complex
        
        # Look for lines containing address components
        address_indicators = [
            r'\d+\s+[A-Za-z0-9\s,]+(?:Road|Rd|Street|St|Avenue|Ave|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Plaza|Plz|Square|Sq)',
            r'\b[A-Z]{2}\s+\d{5}(?:-\d{4})?\b',  # ZIP code pattern
            r'\b(?:Suite|Apt|Apartment|Unit)\s+[A-Za-z0-9-]+\b'
        ]
        
        candidates = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in address_indicators):
                candidates.append(line)
        
        return list(set(candidates))
    
    def is_ad_or_irrelevant(self, text: str) -> bool:
        """
        Checks if text is likely an advertisement or irrelevant content
        
        Args:
            text: The text to check
            
        Returns:
            Boolean indicating if text is likely an ad or irrelevant
        """
        # Common ad and irrelevant content indicators
        ad_indicators = [
            r'\b(?:ad|advertisement|sponsor)\b',
            r'\b(?:click here|sign up|subscribe|free trial)\b',
            r'\b(?:terms of service|privacy policy|cookie policy)\b',
            r'\b(?:all rights reserved|copyright)\b'
        ]
        
        for pattern in ad_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def remove_duplicates(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Removes duplicate items based on content
        
        Args:
            items: List of items to deduplicate
            
        Returns:
            Deduplicated list of items
        """
        # Create a set of content signatures
        seen_content = set()
        unique_items = []
        
        for item in items:
            # Create a signature based on relevant fields
            if "content" in item:
                content = item["content"]
                if isinstance(content, str):
                    # For text content
                    signature = content[:100]  # Use first 100 chars as signature
                elif isinstance(content, list):
                    # For list content
                    signature = str(content)[:100]
                else:
                    # For other content types
                    signature = str(item)[:100]
                
                if signature not in seen_content:
                    seen_content.add(signature)
                    unique_items.append(item)
            else:
                # If no content field, use the whole item as signature
                signature = str(item)[:100]
                if signature not in seen_content:
                    seen_content.add(signature)
                    unique_items.append(item)
        
        return unique_items
    
    def parse_and_categorize(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses and categorizes results from all sources
        
        Args:
            results: Combined raw results from all sources
            
        Returns:
            Dictionary with categorized and filtered results
        """
        categorized = {
            "contact_info": [],
            "social_profiles": [],
            "domain_info": [],
            "breach_data": [],
            "location_data": [],
            "related_links": [],
            "raw_data": []
        }
        
        # Process WHOIS results
        if "whois" in results:
            whois_data = results["whois"]
            
            # Domain WHOIS
            if "domain" in whois_data:
                domain_data = whois_data["domain"]
                
                # Add to domain_info category
                if "domain_name" in domain_data:
                    categorized["domain_info"].append({
                        "title": f"WHOIS Information for {domain_data.get('domain_name', 'Domain')}",
                        "source": "WHOIS",
                        "content_type": "pre",
                        "content": self._format_dict_as_text(domain_data)
                    })
                
                # Extract registrant contact info
                contact_info = {}
                for key in ["registrant_name", "registrant_email", "registrant_phone", "registrant_organization"]:
                    if key in domain_data and domain_data[key]:
                        contact_info[key.replace("registrant_", "")] = domain_data[key]
                
                if contact_info:
                    categorized["contact_info"].append({
                        "title": "Domain Registrant Contact Information",
                        "source": "WHOIS",
                        "content_type": "pre",
                        "content": self._format_dict_as_text(contact_info)
                    })
            
            # IP WHOIS
            if "ip" in whois_data:
                ip_data = whois_data["ip"]
                
                # Add to raw_data category
                categorized["raw_data"].append({
                    "title": f"WHOIS Information for IP {ip_data.get('ip', ip_data.get('query', 'IP'))}",
                    "source": "WHOIS",
                    "content_type": "pre",
                    "content": self._format_dict_as_text(ip_data)
                })
                
                # Extract location data
                location_info = {}
                for key in ["country", "city", "region", "address", "netname", "organization"]:
                    if key in ip_data and ip_data[key]:
                        location_info[key] = ip_data[key]
                
                if location_info:
                    categorized["location_data"].append({
                        "title": "IP Location Information",
                        "source": "WHOIS",
                        "content_type": "pre",
                        "content": self._format_dict_as_text(location_info)
                    })
        
        # Process search engine results
        if "search_engines" in results:
            search_results = results["search_engines"]
            
            # Process DuckDuckGo results
            if "duckduckgo" in search_results:
                ddg_data = search_results["duckduckgo"]
                links = []
                
                for result in ddg_data:
                    # Add to related_links category
                    links.append(f"{result['title']} - {result['url']}")
                    
                    # Check if result might contain contact info
                    if "contact" in result["title"].lower() or "contact" in result["snippet"].lower():
                        categorized["contact_info"].append({
                            "title": result["title"],
                            "source": "DuckDuckGo",
                            "content_type": "text",
                            "content": f"{result['snippet']}\n\nLink: {result['url']}"
                        })
                    
                    # Check if result might contain profile info
                    if any(term in result["title"].lower() or term in result["snippet"].lower() 
                           for term in ["profile", "linkedin", "facebook", "twitter", "social"]):
                        categorized["social_profiles"].append({
                            "title": result["title"],
                            "source": "DuckDuckGo",
                            "content_type": "text",
                            "content": f"{result['snippet']}\n\nLink: {result['url']}"
                        })
                
                if links:
                    categorized["related_links"].append({
                        "title": "Related Links from DuckDuckGo",
                        "source": "DuckDuckGo",
                        "content_type": "list",
                        "content": links
                    })
            
            # Process Bing results
            if "bing" in search_results:
                bing_data = search_results["bing"]
                links = []
                
                for result in bing_data:
                    # Add to related_links category
                    links.append(f"{result['title']} - {result['url']}")
                    
                    # Check if result might contain contact info
                    if "contact" in result["title"].lower() or "contact" in result["snippet"].lower():
                        categorized["contact_info"].append({
                            "title": result["title"],
                            "source": "Bing",
                            "content_type": "text",
                            "content": f"{result['snippet']}\n\nLink: {result['url']}"
                        })
                    
                    # Check if result might contain profile info
                    if any(term in result["title"].lower() or term in result["snippet"].lower() 
                           for term in ["profile", "linkedin", "facebook", "twitter", "social"]):
                        categorized["social_profiles"].append({
                            "title": result["title"],
                            "source": "Bing",
                            "content_type": "text",
                            "content": f"{result['snippet']}\n\nLink: {result['url']}"
                        })
                
                if links:
                    categorized["related_links"].append({
                        "title": "Related Links from Bing",
                        "source": "Bing",
                        "content_type": "list",
                        "content": links
                    })
        
        # Process API results
        if "api_sources" in results:
            api_results = results["api_sources"]
            
            # Process IPinfo results
            if "ipinfo" in api_results:
                ipinfo_data = api_results["ipinfo"]
                
                # Add location data
                location_info = {}
                for key in ["ip", "hostname", "city", "region", "country", "loc", "org", "postal", "timezone"]:
                    if key in ipinfo_data and ipinfo_data[key]:
                        location_info[key] = ipinfo_data[key]
                
                if location_info:
                    categorized["location_data"].append({
                        "title": f"IP Location Information for {ipinfo_data.get('ip', 'IP')}",
                        "source": "IPinfo.io",
                        "content_type": "pre",
                        "content": self._format_dict_as_text(location_info)
                    })
            
            # Process Hunter.io results
            if "hunter" in api_results:
                hunter_data = api_results["hunter"]
                
                # Process domain data
                if "domain" in hunter_data:
                    domain_info = {
                        "domain": hunter_data["domain"],
                        "disposable": hunter_data.get("disposable", False),
                        "webmail": hunter_data.get("webmail", False),
                        "pattern": hunter_data.get("pattern", None)
                    }
                    
                    categorized["domain_info"].append({
                        "title": f"Domain Information for {hunter_data['domain']}",
                        "source": "Hunter.io",
                        "content_type": "pre",
                        "content": self._format_dict_as_text(domain_info)
                    })
                
                # Process email verification data
                if "email" in hunter_data:
                    email_info = {
                        "email": hunter_data["email"],
                        "status": hunter_data.get("status", "unknown"),
                        "disposable": hunter_data.get("disposable", False),
                        "webmail": hunter_data.get("webmail", False),
                        "sources": len(hunter_data.get("sources", []))
                    }
                    
                    categorized["contact_info"].append({
                        "title": f"Email Information for {hunter_data['email']}",
                        "source": "Hunter.io",
                        "content_type": "pre",
                        "content": self._format_dict_as_text(email_info)
                    })
                
                # Process found emails
                if "emails" in hunter_data and hunter_data["emails"]:
                    emails = []
                    for email_entry in hunter_data["emails"]:
                        if "value" in email_entry:
                            email_line = f"{email_entry['value']}"
                            if "first_name" in email_entry and "last_name" in email_entry:
                                email_line += f" - {email_entry['first_name']} {email_entry['last_name']}"
                            if "position" in email_entry:
                                email_line += f" ({email_entry['position']})"
                            emails.append(email_line)
                    
                    if emails:
                        categorized["contact_info"].append({
                            "title": f"Email Addresses Found for {hunter_data.get('domain', 'Domain')}",
                            "source": "Hunter.io",
                            "content_type": "list",
                            "content": emails
                        })
            
            # Process HaveIBeenPwned results
            if "haveibeenpwned" in api_results:
                hibp_data = api_results["haveibeenpwned"]
                
                breaches = []
                for breach in hibp_data:
                    breach_info = {
                        "name": breach.get("Name", "Unknown"),
                        "title": breach.get("Title", "Unknown"),
                        "domain": breach.get("Domain", "Unknown"),
                        "breach_date": breach.get("BreachDate", "Unknown"),
                        "added_date": breach.get("AddedDate", "Unknown"),
                        "modified_date": breach.get("ModifiedDate", "Unknown"),
                        "pwn_count": breach.get("PwnCount", 0),
                        "description": breach.get("Description", "No description available"),
                        "data_classes": ", ".join(breach.get("DataClasses", []))
                    }
                    
                    breaches.append(breach_info)
                
                if breaches:
                    # Format each breach
                    breach_texts = []
                    for breach in breaches:
                        breach_text = f"Name: {breach['name']}\n"
                        breach_text += f"Title: {breach['title']}\n"
                        breach_text += f"Domain: {breach['domain']}\n"
                        breach_text += f"Breach Date: {breach['breach_date']}\n"
                        breach_text += f"Records Exposed: {breach['pwn_count']}\n"
                        breach_text += f"Data Compromised: {breach['data_classes']}\n"
                        breach_text += f"Description: {breach['description']}"
                        breach_texts.append(breach_text)
                    
                    categorized["breach_data"].append({
                        "title": f"Data Breaches ({len(breaches)} found)",
                        "source": "Have I Been Pwned",
                        "content_type": "list",
                        "content": breach_texts
                    })
        
        # Remove duplicates from each category
        for category in categorized:
            categorized[category] = self.remove_duplicates(categorized[category])
        
        return categorized
    
    def generate_summary(self, categorized_results: Dict[str, List]) -> str:
        """
        Generates a bullet-point executive summary of the findings
        
        Args:
            categorized_results: The categorized results dictionary
            
        Returns:
            String containing the executive summary
        """
        summary_lines = []
        
        # Count items in each category
        contact_count = len(categorized_results.get("contact_info", []))
        social_count = len(categorized_results.get("social_profiles", []))
        domain_count = len(categorized_results.get("domain_info", []))
        breach_count = len(categorized_results.get("breach_data", []))
        location_count = len(categorized_results.get("location_data", []))
        links_count = len(categorized_results.get("related_links", []))
        
        # Create summary based on found information
        if contact_count > 0:
            summary_lines.append(f"• Found <b>{contact_count}</b> contact information items")
        
        if social_count > 0:
            summary_lines.append(f"• Identified <b>{social_count}</b> social profile references")
        
        if domain_count > 0:
            summary_lines.append(f"• Collected <b>{domain_count}</b> domain information records")
        
        if breach_count > 0:
            summary_lines.append(f"• Discovered <b>{breach_count}</b> data breach records")
        
        if location_count > 0:
            summary_lines.append(f"• Located <b>{location_count}</b> geographical location references")
        
        if links_count > 0:
            related_links_count = sum(len(item.get("content", [])) for item in categorized_results.get("related_links", []) if isinstance(item.get("content"), list))
            summary_lines.append(f"• Found <b>{related_links_count}</b> related links from search engines")
        
        # If no information found
        if not summary_lines:
            summary_lines.append("• No significant information found for the provided query")
            summary_lines.append("• Consider trying a different query or enabling additional data sources")
        
        return "<br>".join(summary_lines)
    
    def _format_dict_as_text(self, data: Dict[str, Any]) -> str:
        """
        Formats a dictionary as readable text
        
        Args:
            data: Dictionary to format
            
        Returns:
            Formatted text representation
        """
        lines = []
        for key, value in data.items():
            # Format key for display
            display_key = key.replace("_", " ").title()
            
            # Format value based on type
            if isinstance(value, list):
                if value and isinstance(value[0], dict):
                    # List of dictionaries
                    lines.append(f"{display_key}:")
                    for item in value:
                        lines.append("  - " + self._format_dict_as_text(item).replace("\n", "\n    "))
                else:
                    # Simple list
                    lines.append(f"{display_key}: {', '.join(str(item) for item in value)}")
            elif isinstance(value, dict):
                # Dictionary
                lines.append(f"{display_key}:")
                nested_text = self._format_dict_as_text(value)
                lines.append("  " + nested_text.replace("\n", "\n  "))
            else:
                # Simple value
                lines.append(f"{display_key}: {value}")
        
        return "\n".join(lines)