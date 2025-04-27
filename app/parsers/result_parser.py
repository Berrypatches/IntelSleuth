import logging
import re
from typing import Dict, List, Any, Set
import json

logger = logging.getLogger(__name__)

class ResultParser:
    """
    Parses, filters and categorizes the raw results from various sources
    """
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """
        Extracts email addresses from text
        
        Args:
            text: The text to extract emails from
            
        Returns:
            List of extracted email addresses
        """
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        return list(set(emails))
    
    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """
        Extracts phone numbers from text
        
        Args:
            text: The text to extract phone numbers from
            
        Returns:
            List of extracted phone numbers
        """
        # Pattern for phone numbers (various formats)
        phone_pattern = r'(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?'
        phones = re.findall(phone_pattern, text)
        
        # Format the extracted phone numbers
        formatted_phones = []
        for phone_parts in phones:
            # Filter out empty parts and join
            parts = [part for part in phone_parts if part]
            if parts:
                formatted_phone = '-'.join(parts)
                formatted_phones.append(formatted_phone)
        
        return list(set(formatted_phones))
    
    @staticmethod
    def extract_social_links(text: str) -> List[str]:
        """
        Extracts social media links from text
        
        Args:
            text: The text to extract social links from
            
        Returns:
            List of extracted social media links
        """
        # Pattern for common social media URLs
        social_pattern = r'https?://(?:www\.)?(?:facebook\.com|twitter\.com|linkedin\.com|instagram\.com|github\.com)/[a-zA-Z0-9_\-./]+'
        social_links = re.findall(social_pattern, text)
        return list(set(social_links))
    
    @staticmethod
    def extract_addresses(text: str) -> List[str]:
        """
        Extracts physical addresses from text (simplified version)
        
        Args:
            text: The text to extract addresses from
            
        Returns:
            List of extracted address candidates
        """
        # This is a simplified pattern - real address extraction is complex
        # and might require NLP or specialized libraries
        address_pattern = r'\d+\s+[A-Za-z0-9\s,]+(?:Avenue|Ave|Street|St|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\.?(?:\s+[A-Za-z]+,\s+[A-Za-z]+\s+\d{5}(?:-\d{4})?)?'
        addresses = re.findall(address_pattern, text, re.IGNORECASE)
        return list(set(addresses))
    
    @staticmethod
    def is_ad_or_irrelevant(text: str) -> bool:
        """
        Checks if text is likely an advertisement or irrelevant content
        
        Args:
            text: The text to check
            
        Returns:
            Boolean indicating if text is likely an ad or irrelevant
        """
        ad_indicators = [
            'sponsored', 'advertisement', 'ads', 'promoted',
            'buy now', 'limited time offer', 'discount', 'sale',
            'click here', 'sign up now', 'subscribe', 'free trial'
        ]
        
        lower_text = text.lower()
        
        # Check for ad indicators
        for indicator in ad_indicators:
            if indicator in lower_text:
                return True
        
        return False
    
    @staticmethod
    def remove_duplicates(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Removes duplicate items based on content
        
        Args:
            items: List of items to deduplicate
            
        Returns:
            Deduplicated list of items
        """
        unique_items = []
        seen_content = set()
        
        for item in items:
            # Create a fingerprint of the item's core content
            if "title" in item and "url" in item:
                # For search results
                fingerprint = f"{item['title']}|{item['url']}"
            elif "name" in item and "email" in item:
                # For contact info
                fingerprint = f"{item['name']}|{item['email']}"
            else:
                # For other types, convert to JSON string
                fingerprint = json.dumps(item, sort_keys=True)
            
            if fingerprint not in seen_content:
                seen_content.add(fingerprint)
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
            "emails": [],
            "phone_numbers": [],
            "social_links": [],
            "addresses": [],
            "business_info": [],
            "leaks": [],
            "raw_results": [],
            "domains": [],
            "ips": []
        }
        
        # Process search engine results
        if "search_results" in results:
            for source, items in results["search_results"].items():
                for item in items:
                    # Skip ads and irrelevant content
                    if self.is_ad_or_irrelevant(item.get("title", "") + " " + item.get("snippet", "")):
                        continue
                    
                    # Add to raw results
                    categorized["raw_results"].append(item)
                    
                    # Extract various entities from snippet
                    snippet = item.get("snippet", "")
                    
                    # Extract and add emails
                    emails = self.extract_emails(snippet)
                    for email in emails:
                        categorized["emails"].append({
                            "email": email,
                            "source": item.get("source", "unknown"),
                            "context": item.get("title", "")
                        })
                    
                    # Extract and add phone numbers
                    phones = self.extract_phone_numbers(snippet)
                    for phone in phones:
                        categorized["phone_numbers"].append({
                            "phone": phone,
                            "source": item.get("source", "unknown"),
                            "context": item.get("title", "")
                        })
                    
                    # Extract and add social links
                    social = self.extract_social_links(snippet)
                    for link in social:
                        categorized["social_links"].append({
                            "url": link,
                            "source": item.get("source", "unknown"),
                            "context": item.get("title", "")
                        })
                    
                    # Extract and add addresses
                    addresses = self.extract_addresses(snippet)
                    for address in addresses:
                        categorized["addresses"].append({
                            "address": address,
                            "source": item.get("source", "unknown"),
                            "context": item.get("title", "")
                        })
        
        # Process API results
        if "api_results" in results:
            # Process IPinfo results
            if "ipinfo" in results["api_results"]:
                ipinfo = results["api_results"]["ipinfo"]
                if "error" not in ipinfo:
                    categorized["ips"].append({
                        "ip": ipinfo.get("ip", ""),
                        "hostname": ipinfo.get("hostname", ""),
                        "city": ipinfo.get("city", ""),
                        "region": ipinfo.get("region", ""),
                        "country": ipinfo.get("country", ""),
                        "loc": ipinfo.get("loc", ""),
                        "org": ipinfo.get("org", ""),
                        "postal": ipinfo.get("postal", ""),
                        "timezone": ipinfo.get("timezone", ""),
                        "source": "ipinfo"
                    })
                    
                    # Add business info if organization is present
                    if "org" in ipinfo and ipinfo["org"]:
                        categorized["business_info"].append({
                            "name": ipinfo["org"],
                            "source": "ipinfo",
                            "type": "hosting_provider"
                        })
            
            # Process Hunter.io results
            if "hunter" in results["api_results"]:
                hunter = results["api_results"]["hunter"]
                if "error" not in hunter:
                    # For domain search results
                    if "emails" in hunter:
                        for email in hunter.get("emails", []):
                            categorized["emails"].append({
                                "email": email.get("value", ""),
                                "name": f"{email.get('first_name', '')} {email.get('last_name', '')}".strip(),
                                "position": email.get("position", ""),
                                "confidence": email.get("confidence", 0),
                                "source": "hunter"
                            })
                        
                        # Add domain info
                        if "domain" in hunter:
                            categorized["domains"].append({
                                "domain": hunter["domain"],
                                "organization": hunter.get("organization", ""),
                                "source": "hunter"
                            })
                        
                        # Add business info if organization is present
                        if "organization" in hunter and hunter["organization"]:
                            categorized["business_info"].append({
                                "name": hunter["organization"],
                                "domain": hunter.get("domain", ""),
                                "email_pattern": hunter.get("pattern", ""),
                                "source": "hunter"
                            })
                    
                    # For email verification results
                    elif "email" in hunter:
                        categorized["emails"].append({
                            "email": hunter["email"],
                            "name": f"{hunter.get('first_name', '')} {hunter.get('last_name', '')}".strip(),
                            "score": hunter.get("score", 0),
                            "status": hunter.get("status", ""),
                            "source": "hunter"
                        })
            
            # Process HaveIBeenPwned results
            if "haveibeenpwned" in results["api_results"]:
                hibp = results["api_results"]["haveibeenpwned"]
                for breach in hibp:
                    if "error" not in breach:
                        categorized["leaks"].append({
                            "name": breach.get("Name", ""),
                            "title": breach.get("Title", ""),
                            "domain": breach.get("Domain", ""),
                            "breach_date": breach.get("BreachDate", ""),
                            "description": breach.get("Description", ""),
                            "data_classes": breach.get("DataClasses", []),
                            "source": "haveibeenpwned"
                        })
        
        # Process WHOIS results
        if "whois_results" in results and "whois" in results["whois_results"]:
            whois_data = results["whois_results"]["whois"]
            if "error" not in whois_data:
                # For domain WHOIS
                if "domain_name" in whois_data:
                    categorized["domains"].append({
                        "domain": whois_data.get("domain_name", ""),
                        "registrar": whois_data.get("registrar", ""),
                        "creation_date": whois_data.get("creation_date", ""),
                        "expiration_date": whois_data.get("expiration_date", ""),
                        "name_servers": whois_data.get("name_servers", []),
                        "source": "whois"
                    })
                    
                    # Add emails from WHOIS if present
                    for email in whois_data.get("emails", []):
                        categorized["emails"].append({
                            "email": email,
                            "relation": "domain registrant or admin",
                            "source": "whois"
                        })
                
                # For IP WHOIS
                elif "ip" in whois_data:
                    categorized["ips"].append({
                        "ip": whois_data.get("ip", ""),
                        "hostname": whois_data.get("hostname", ""),
                        "source": "whois"
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
        summary_lines = ["# Executive Summary"]
        
        # Add email findings
        emails = categorized_results.get("emails", [])
        if emails:
            summary_lines.append(f"\n## Emails ({len(emails)} found)")
            for email in emails[:5]:  # Limit to top 5 for summary
                email_str = email.get("email", "")
                name = email.get("name", "")
                position = email.get("position", "")
                
                email_info = f"* {email_str}"
                if name:
                    email_info += f" - {name}"
                if position:
                    email_info += f" ({position})"
                
                summary_lines.append(email_info)
            
            if len(emails) > 5:
                summary_lines.append(f"* ... and {len(emails) - 5} more")
        
        # Add phone findings
        phones = categorized_results.get("phone_numbers", [])
        if phones:
            summary_lines.append(f"\n## Phone Numbers ({len(phones)} found)")
            for phone in phones[:5]:  # Limit to top 5 for summary
                phone_str = phone.get("phone", "")
                context = phone.get("context", "")
                
                phone_info = f"* {phone_str}"
                if context:
                    phone_info += f" - {context}"
                
                summary_lines.append(phone_info)
            
            if len(phones) > 5:
                summary_lines.append(f"* ... and {len(phones) - 5} more")
        
        # Add social findings
        socials = categorized_results.get("social_links", [])
        if socials:
            summary_lines.append(f"\n## Social Media ({len(socials)} found)")
            for social in socials[:5]:  # Limit to top 5 for summary
                url = social.get("url", "")
                # Extract platform name from URL
                platform = "Unknown"
                if "facebook.com" in url:
                    platform = "Facebook"
                elif "twitter.com" in url:
                    platform = "Twitter"
                elif "linkedin.com" in url:
                    platform = "LinkedIn"
                elif "instagram.com" in url:
                    platform = "Instagram"
                elif "github.com" in url:
                    platform = "GitHub"
                
                summary_lines.append(f"* {platform}: {url}")
            
            if len(socials) > 5:
                summary_lines.append(f"* ... and {len(socials) - 5} more")
        
        # Add domain findings
        domains = categorized_results.get("domains", [])
        if domains:
            summary_lines.append(f"\n## Domains ({len(domains)} found)")
            for domain in domains[:5]:  # Limit to top 5 for summary
                domain_str = domain.get("domain", "")
                if isinstance(domain_str, list):
                    domain_str = domain_str[0]  # Use first domain if it's a list
                
                registrar = domain.get("registrar", "")
                creation = domain.get("creation_date", "")
                
                domain_info = f"* {domain_str}"
                if registrar:
                    domain_info += f" - Registrar: {registrar}"
                if creation and not isinstance(creation, list):
                    domain_info += f" - Created: {creation}"
                
                summary_lines.append(domain_info)
        
        # Add IP findings
        ips = categorized_results.get("ips", [])
        if ips:
            summary_lines.append(f"\n## IP Addresses ({len(ips)} found)")
            for ip in ips[:5]:  # Limit to top 5 for summary
                ip_str = ip.get("ip", "")
                org = ip.get("org", "")
                location = ""
                
                if ip.get("city") and ip.get("country"):
                    location = f"{ip.get('city')}, {ip.get('country')}"
                
                ip_info = f"* {ip_str}"
                if location:
                    ip_info += f" - Location: {location}"
                if org:
                    ip_info += f" - Organization: {org}"
                
                summary_lines.append(ip_info)
        
        # Add leak findings
        leaks = categorized_results.get("leaks", [])
        if leaks:
            summary_lines.append(f"\n## Data Breaches ({len(leaks)} found)")
            for leak in leaks[:5]:  # Limit to top 5 for summary
                name = leak.get("name", "")
                date = leak.get("breach_date", "")
                classes = leak.get("data_classes", [])
                
                leak_info = f"* {name}"
                if date:
                    leak_info += f" ({date})"
                if classes:
                    leak_info += f" - Data exposed: {', '.join(classes[:3])}"
                    if len(classes) > 3:
                        leak_info += f" and {len(classes) - 3} more"
                
                summary_lines.append(leak_info)
            
            if len(leaks) > 5:
                summary_lines.append(f"* ... and {len(leaks) - 5} more")
        
        # Add business findings
        businesses = categorized_results.get("business_info", [])
        if businesses:
            summary_lines.append(f"\n## Business Information ({len(businesses)} found)")
            for business in businesses[:5]:  # Limit to top 5 for summary
                name = business.get("name", "")
                domain = business.get("domain", "")
                
                business_info = f"* {name}"
                if domain:
                    business_info += f" - Domain: {domain}"
                
                summary_lines.append(business_info)
        
        # Add address findings
        addresses = categorized_results.get("addresses", [])
        if addresses:
            summary_lines.append(f"\n## Addresses ({len(addresses)} found)")
            for address in addresses[:5]:  # Limit to top 5 for summary
                addr = address.get("address", "")
                context = address.get("context", "")
                
                address_info = f"* {addr}"
                if context:
                    address_info += f" - Context: {context}"
                
                summary_lines.append(address_info)
            
            if len(addresses) > 5:
                summary_lines.append(f"* ... and {len(addresses) - 5} more")
        
        # If no findings
        if len(summary_lines) <= 1:
            summary_lines.append("\nNo significant findings.")
        
        return "\n".join(summary_lines)
