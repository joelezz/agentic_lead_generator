"""
Email extraction tool for finding decision-maker contact information.
"""
import re
import logging
from typing import List, Optional, Dict

from crewai_tools import BaseTool

logger = logging.getLogger(__name__)


class EmailExtractorTool(BaseTool):
    """Tool for extracting and identifying decision-maker email addresses."""
    
    name: str = "Email Extractor Tool"
    description: str = "Extract email addresses from website content and identify decision-maker contacts"
    
    def __init__(self):
        super().__init__()
        # Common decision-maker titles and keywords
        self.decision_maker_keywords = [
            'ceo', 'founder', 'co-founder', 'owner', 'president', 'director',
            'managing director', 'chief executive', 'principal', 'partner',
            'head of', 'cmo', 'vp'
        ]
        
        # Common generic/non-decision-maker email patterns to deprioritize
        self.generic_patterns = [
            'info@', 'contact@', 'hello@', 'support@', 'sales@',
            'admin@', 'office@', 'team@', 'mail@', 'general@'
        ]
    
    def _run(self, html_content: str, context: str = "") -> Dict:
        """
        Extract emails from HTML content and identify decision-maker.
        
        Args:
            html_content: HTML content to parse
            context: Additional context text (e.g., page text) to help identify decision-maker
            
        Returns:
            Dictionary with 'all_emails' list and 'decision_maker_email' string
        """
        all_emails = self.extract_emails(html_content)
        decision_maker = self.find_decision_maker_email(all_emails, context)
        
        return {
            'all_emails': all_emails,
            'decision_maker_email': decision_maker
        }
    
    def extract_emails(self, html_content: str) -> List[str]:
        """
        Extract email addresses from HTML content using regex patterns.
        
        Args:
            html_content: HTML or text content to parse
            
        Returns:
            List of unique email addresses found
        """
        # Email regex pattern - matches standard email format
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Find all email matches
        emails = re.findall(email_pattern, html_content, re.IGNORECASE)
        
        # Remove duplicates and convert to lowercase
        unique_emails = list(set(email.lower() for email in emails))
        
        # Filter out common spam traps and invalid patterns
        filtered_emails = []
        for email in unique_emails:
            # Skip emails with common placeholder patterns
            if any(placeholder in email for placeholder in ['example.com', 'domain.com', 'email.com', 'test.com']):
                continue
            
            # Skip emails that look like image files or other non-email patterns
            if email.endswith(('.png', '.jpg', '.gif', '.svg')):
                continue
            
            filtered_emails.append(email)
        
        logger.info(f"Extracted {len(filtered_emails)} valid email addresses")
        return filtered_emails
    
    def find_decision_maker_email(self, emails: List[str], context: str) -> Optional[str]:
        """
        Identify the most likely decision-maker email from a list of emails.
        
        Args:
            emails: List of email addresses
            context: Additional context text to help identify decision-maker
            
        Returns:
            Most likely decision-maker email or None if not found
        """
        if not emails:
            logger.warning("No emails provided to identify decision-maker")
            return None
        
        context_lower = context.lower() if context else ""
        scored_emails = []
        
        for email in emails:
            score = 0
            email_lower = email.lower()
            email_local = email_lower.split('@')[0]  # Part before @
            
            # Deprioritize generic emails
            if any(pattern in email_lower for pattern in self.generic_patterns):
                score -= 10
            
            # Check if email local part contains decision-maker keywords
            for keyword in self.decision_maker_keywords:
                if keyword.replace(' ', '') in email_local or keyword.replace(' ', '.') in email_local:
                    score += 15
            
            # Check if email appears near decision-maker keywords in context
            if context_lower:
                # Look for email mentioned near decision-maker titles
                for keyword in self.decision_maker_keywords:
                    # Create a pattern to find keyword near email
                    pattern = f"{keyword}.{{0,100}}{re.escape(email_lower)}"
                    if re.search(pattern, context_lower):
                        score += 10
                    
                    # Also check reverse (email before keyword)
                    pattern_reverse = f"{re.escape(email_lower)}.{{0,100}}{keyword}"
                    if re.search(pattern_reverse, context_lower):
                        score += 10
            
            # Prefer shorter, simpler email addresses (likely personal)
            # firstname@domain or firstname.lastname@domain
            parts = email_local.split('.')
            if len(parts) <= 2 and len(email_local) < 20:
                score += 5
            
            # Prefer emails with common name patterns
            if re.match(r'^[a-z]+\.[a-z]+@', email_lower):  # firstname.lastname@
                score += 8
            elif re.match(r'^[a-z]+@', email_lower):  # firstname@
                score += 6
            
            scored_emails.append((email, score))
        
        # Sort by score (highest first)
        scored_emails.sort(key=lambda x: x[1], reverse=True)
        
        # Log scoring for debugging
        for email, score in scored_emails[:3]:
            logger.debug(f"Email: {email}, Score: {score}")
        
        # Return highest scored email if it has a positive score
        best_email, best_score = scored_emails[0]
        
        if best_score > 0:
            logger.info(f"Identified decision-maker email: {best_email} (score: {best_score})")
            return best_email
        else:
            # If no email has positive score, return first non-generic email
            for email, score in scored_emails:
                if not any(pattern in email.lower() for pattern in self.generic_patterns):
                    logger.info(f"Returning best available email: {email}")
                    return email
            
            # Last resort: return first email
            logger.info(f"Returning first available email: {best_email}")
            return best_email
