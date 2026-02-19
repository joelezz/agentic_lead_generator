"""
Contact Finder Agent

This agent is responsible for finding decision-maker contact information from agency websites.
It searches contact pages, extracts names and email addresses, and identifies the most relevant
decision-maker contact (CEO, Founder, etc.).
"""

import logging
from typing import List, Dict
from crewai import Agent, Task
from tools.web_search_tool import WebScraperTool
from tools.email_finder_tool import EmailExtractorTool

logger = logging.getLogger(__name__)


def create_contact_agent(llm) -> Agent:
    """
    Create the Contact Finder agent.
    
    Args:
        llm: Language model instance for the agent
        
    Returns:
        Agent: Configured Contact Finder agent
    """
    return Agent(
        role="Contact Research Specialist",
        goal="Find decision-maker contact information including names and email addresses from agency websites",
        backstory=(
            "You are an expert at finding contact information for business decision-makers. "
            "You know how to navigate agency websites to locate contact pages, team pages, and "
            "about pages where key personnel are listed. You have a keen eye for identifying "
            "CEOs, Founders, and other decision-makers from website content. You understand that "
            "not all websites will have publicly available contact information, and you handle "
            "such cases gracefully by documenting what you find. Your specialty is extracting "
            "accurate contact details while respecting privacy and data protection practices."
        ),
        tools=[WebScraperTool(), EmailExtractorTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )


def create_contact_task(agent: Agent, agencies: List[Dict]) -> Task:
    """
    Create the task for the Contact Finder agent.
    
    Args:
        agent: The Contact Finder agent
        agencies: List of enriched agencies with name, website, country, and enrichment data
        
    Returns:
        Task: Configured task for contact information discovery
    """
    return Task(
        description=(
            f"Find decision-maker contact information for the following agencies:\n\n"
            f"{agencies}\n\n"
            f"For each agency, use the available tools to:\n"
            f"1. Use the Web Scraper Tool to find and access the contact page\n"
            f"2. Search for team pages, about pages, or leadership sections\n"
            f"3. Use the Email Extractor Tool to extract email addresses from the page content\n"
            f"4. Identify the decision-maker (CEO, Founder, Owner, Managing Director)\n"
            f"5. Extract both the name and email address of the decision-maker\n\n"
            f"Guidelines:\n"
            f"- Prioritize finding CEO, Founder, Co-Founder, or Owner contacts\n"
            f"- Look for contact pages, team pages, about pages, and leadership sections\n"
            f"- Extract the full name of the decision-maker when available\n"
            f"- Use the Email Extractor Tool to identify the most relevant email address\n"
            f"- If no contact information is found, leave contact_name and email fields empty\n"
            f"- Mark contact_status as 'found' if contact info is discovered, 'not_found' if not\n"
            f"- Handle inaccessible websites gracefully - mark as 'not_found' and continue\n"
            f"- Be thorough but efficient - check main contact areas of the website\n\n"
            f"Handle errors gracefully - if you cannot access a website or find contact info, "
            f"continue with the next agency."
        ),
        expected_output=(
            f"A list of agencies with contact information in JSON format:\n"
            f"[\n"
            f"  {{\n"
            f'    "agency_name": "Agency Name",\n'
            f'    "website": "https://agency-website.com",\n'
            f'    "country": "Country",\n'
            f'    "services": "Social Media Management, Content Creation",\n'
            f'    "niche": "ecommerce",\n'
            f'    "notes": "Team of 15+",\n'
            f'    "enrichment_status": "complete",\n'
            f'    "contact_name": "John Smith",\n'
            f'    "email": "john@agency-website.com",\n'
            f'    "contact_status": "found"\n'
            f"  }}\n"
            f"]\n"
            f"Each agency must include all previous fields plus contact_name, email, and contact_status. "
            f"If contact information is not found, leave contact_name and email as empty strings."
        ),
        agent=agent
    )


def run_contact_agent(agencies: List[Dict], llm) -> List[Dict]:
    """
    Execute the Contact Finder agent to discover decision-maker contact information.
    
    Args:
        agencies: List of enriched agencies with business intelligence
        llm: Language model instance
        
    Returns:
        List[Dict]: List of agencies with contact information added
    """
    logger.info(f"Starting contact discovery for {len(agencies)} agencies")
    
    # Create agent and task
    agent = create_contact_agent(llm)
    task = create_contact_task(agent, agencies)
    
    # Execute task
    try:
        result = agent.execute_task(task)
        
        # Count successful contact discoveries
        found_count = sum(1 for a in result if a.get('contact_status') == 'found')
        logger.info(f"Contact discovery completed. {found_count}/{len(agencies)} contacts found")
        
        return result
    except Exception as e:
        logger.error(f"Error during contact discovery: {e}")
        
        # Return agencies with not_found status on error
        agencies_with_contact_status = []
        for agency in agencies:
            agency_with_status = agency.copy()
            agency_with_status.update({
                'contact_name': '',
                'email': '',
                'contact_status': 'not_found'
            })
            agencies_with_contact_status.append(agency_with_status)
        
        return agencies_with_contact_status
