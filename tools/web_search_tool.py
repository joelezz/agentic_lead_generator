"""
Web scraping tools for agency discovery and content extraction.
"""
import re
import time
import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from crewai_tools import BaseTool

logger = logging.getLogger(__name__)


class WebSearchTool(BaseTool):
    """Tool for searching and discovering marketing agencies."""
    
    name: str = "Web Search Tool"
    description: str = "Search for marketing agencies across multiple sources including Clutch.co, Sortlist, and Google Maps"
    
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _run(self, country: str, query: str = "social media marketing agency", max_results: int = 10) -> List[Dict]:
        """
        Search for agencies in the specified country.
        
        Args:
            country: Target country for agency search
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of dictionaries with agency_name, website, and country
        """
        agencies = []
        
        # Search Clutch.co
        try:
            clutch_results = self.search_clutch(country, query, max_results)
            agencies.extend(clutch_results)
            logger.info(f"Found {len(clutch_results)} agencies from Clutch.co")
        except Exception as e:
            logger.error(f"Error searching Clutch.co: {e}")
        
        # Add delay between searches
        time.sleep(2)
        
        # Search Sortlist
        try:
            sortlist_results = self.search_sortlist(country, query, max_results)
            agencies.extend(sortlist_results)
            logger.info(f"Found {len(sortlist_results)} agencies from Sortlist")
        except Exception as e:
            logger.error(f"Error searching Sortlist: {e}")
        
        # Remove duplicates based on website
        seen_websites = set()
        unique_agencies = []
        for agency in agencies:
            if agency['website'] not in seen_websites:
                seen_websites.add(agency['website'])
                unique_agencies.append(agency)
        
        return unique_agencies[:max_results]
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def search_clutch(self, country: str, query: str, max_results: int) -> List[Dict]:
        """Search Clutch.co for agencies."""
        agencies = []
        country_slug = country.lower().replace(' ', '-')
        
        # Clutch.co URL pattern
        url = f"https://clutch.co/agencies/social-media-marketing/{country_slug}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse agency listings
            listings = soup.find_all('div', class_='provider-info')
            
            for listing in listings[:max_results]:
                try:
                    name_elem = listing.find('h3', class_='company_title')
                    website_elem = listing.find('a', class_='website-link')
                    
                    if name_elem and website_elem:
                        agencies.append({
                            'agency_name': name_elem.get_text(strip=True),
                            'website': website_elem.get('href', ''),
                            'country': country
                        })
                except Exception as e:
                    logger.warning(f"Error parsing Clutch listing: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error fetching from Clutch.co: {e}")
        
        return agencies
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def search_sortlist(self, country: str, query: str, max_results: int) -> List[Dict]:
        """Search Sortlist for agencies."""
        agencies = []
        country_slug = country.lower().replace(' ', '-')
        
        # Sortlist URL pattern
        url = f"https://www.sortlist.com/s/{country_slug}/social-media-marketing"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse agency listings
            listings = soup.find_all('div', class_='agency-card')
            
            for listing in listings[:max_results]:
                try:
                    name_elem = listing.find('h3')
                    link_elem = listing.find('a', href=True)
                    
                    if name_elem and link_elem:
                        # Extract website from agency profile page
                        profile_url = urljoin(url, link_elem['href'])
                        website = self._extract_website_from_profile(profile_url)
                        
                        if website:
                            agencies.append({
                                'agency_name': name_elem.get_text(strip=True),
                                'website': website,
                                'country': country
                            })
                        
                        time.sleep(1)  # Rate limiting
                        
                except Exception as e:
                    logger.warning(f"Error parsing Sortlist listing: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error fetching from Sortlist: {e}")
        
        return agencies
    
    def _extract_website_from_profile(self, profile_url: str) -> Optional[str]:
        """Extract website URL from agency profile page."""
        try:
            response = self.session.get(profile_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for website link
            website_link = soup.find('a', {'rel': 'nofollow noopener', 'target': '_blank'})
            if website_link and website_link.get('href'):
                return website_link['href']
                
        except Exception as e:
            logger.warning(f"Error extracting website from profile: {e}")
        
        return None


class WebScraperTool(BaseTool):
    """Tool for scraping content from agency websites."""
    
    name: str = "Web Scraper Tool"
    description: str = "Scrape and extract content from agency websites including text, links, and contact information"
    
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _run(self, url: str) -> Dict:
        """
        Scrape website content.
        
        Args:
            url: Website URL to scrape
            
        Returns:
            Dictionary with text_content, links, and contact_page_url
        """
        return self.scrape_website(url)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def scrape_website(self, url: str) -> Dict:
        """
        Scrape website content and structure.
        
        Args:
            url: Website URL to scrape
            
        Returns:
            Dictionary containing:
                - text_content: Main text content from the page
                - links: List of internal links
                - contact_page_url: URL of contact page if found
        """
        result = {
            'text_content': '',
            'links': [],
            'contact_page_url': None
        }
        
        try:
            # Add rate limiting delay
            time.sleep(1.5)
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()
            
            # Extract text content
            text = soup.get_text(separator=' ', strip=True)
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            result['text_content'] = text[:5000]  # Limit to first 5000 chars
            
            # Extract links
            base_domain = urlparse(url).netloc
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(url, href)
                
                # Only include internal links
                if urlparse(absolute_url).netloc == base_domain:
                    links.append({
                        'url': absolute_url,
                        'text': link.get_text(strip=True)
                    })
            
            result['links'] = links
            
            # Find contact page
            contact_url = self.extract_contact_page(url, soup)
            result['contact_page_url'] = contact_url
            
            logger.info(f"Successfully scraped {url}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error scraping {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            raise
        
        return result
    
    def extract_contact_page(self, base_url: str, soup: BeautifulSoup) -> Optional[str]:
        """
        Find contact page URL from website.
        
        Args:
            base_url: Base URL of the website
            soup: BeautifulSoup object of the page
            
        Returns:
            Contact page URL if found, None otherwise
        """
        contact_keywords = [
            'contact', 'kontakt', 'yhteystiedot', 'get-in-touch',
            'reach-us', 'contact-us', 'contacto', 'contato'
        ]
        
        # Search for contact links
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            link_text = link.get_text(strip=True).lower()
            
            # Check if link contains contact keywords
            for keyword in contact_keywords:
                if keyword in href or keyword in link_text:
                    contact_url = urljoin(base_url, link['href'])
                    logger.info(f"Found contact page: {contact_url}")
                    return contact_url
        
        # Try common contact page paths
        common_paths = ['/contact', '/contact-us', '/get-in-touch', '/kontakt']
        base_domain = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}"
        
        for path in common_paths:
            try:
                test_url = base_domain + path
                time.sleep(1)  # Rate limiting
                
                response = self.session.head(test_url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    logger.info(f"Found contact page at common path: {test_url}")
                    return test_url
            except Exception:
                continue
        
        logger.warning(f"No contact page found for {base_url}")
        return None
