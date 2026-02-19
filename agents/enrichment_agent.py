"""
Enrichment Agent

This agent is responsible for analyzing agency websites to extract business intelligence
including services offered, niche/specialization, and company size signals. It enriches
the basic agency information with detailed business context.
"""

import logging
from typing import List, Dict
from crewai import Agent, Task
from tools.web_search_tool import WebScraperTool

logger = logging.getLogger(__name__)


def create_enrichment_agent(llm) -> Agent:
    """
    Create the Enrichment agent.
    
    Args:
        llm: Language model instance for the agent
        
    Returns:
        Agent: Configured Enrichment agent
    """
    return Agent(
        role="Business Intelligence Analyst",
        goal="Analyze agency websites to extract services, niche, and company size signals for lead enrichment",
        backstory=(
            "You are a skilled business analyst who specializes in understanding marketing agencies. "
            "You have a keen eye for identifying what services an agency offers, what industries they "
            "specialize in, and how large their operation is based on website content. You can quickly "
            "scan through website copy, case studies, and team pages to extract meaningful business "
            "intelligence. You understand marketing terminology and can categorize agencies accurately "
            "based on their positioning and service offerings."
        ),
        tools=[WebScraperTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )


def create_enrichment_task(agent: Agent, agencies: List[Dict]) -> Task:
    """
    Create the task for the Enrichment agent.
    
    Args:
        agent: The Enrichment agent
        agencies: List of agencies to enrich with name, website, and country
        
    Returns:
        Task: Configured task for agency enrichment
    """
    return Task(
        description=(
            f"Analyze the websites of the following agencies to extract business intelligence:\n\n"
            f"{agencies}\n\n"
            f"For each agency, use the Web Scraper Tool to:\n"
            f"1. Scrape the agency website content\n"
            f"2. Analyze the content to identify:\n"
            f"   - Services offered (e.g., 'Social Media Management, Content Creation, Paid Advertising')\n"
            f"   - Niche/specialization (e.g., 'ecommerce', 'B2B SaaS', 'local business', 'healthcare')\n"
            f"   - Company size signals (look for team size, client count, years in business)\n\n"
            f"Guidelines:\n"
            f"- Extract specific services from the website (look in services pages, about pages)\n"
            f"- Identify the primary niche based on case studies, client testimonials, or positioning\n"
            f"- Note any company size indicators in the notes field\n"
            f"- If a website is inaccessible or returns errors, mark enrichment_status as 'incomplete'\n"
            f"- If enrichment is successful, mark enrichment_status as 'complete'\n"
            f"- Be concise but specific in your descriptions\n\n"
            f"Handle errors gracefully - if you cannot access a website, continue with the next agency."
        ),
        expected_output=(
            f"A list of enriched agencies in JSON format with the following structure:\n"
            f"[\n"
            f"  {{\n"
            f'    "agency_name": "Agency Name",\n'
            f'    "website": "https://agency-website.com",\n'
            f'    "country": "Country",\n'
            f'    "services": "Social Media Management, Content Creation, Paid Advertising",\n'
            f'    "niche": "ecommerce",\n'
            f'    "notes": "Team of 15+, 5 years in business, 100+ clients",\n'
            f'    "enrichment_status": "complete"\n'
            f"  }}\n"
            f"]\n"
            f"Each agency must include all original fields plus services, niche, notes, and enrichment_status."
        ),
        agent=agent
    )


def run_enrichment_agent(agencies: List[Dict], llm) -> List[Dict]:
    """
    Execute the Enrichment agent to analyze and enrich agency data.
    
    Args:
        agencies: List of agencies with name, website, and country
        llm: Language model instance
        
    Returns:
        List[Dict]: List of enriched agencies with additional business intelligence
    """
    logger.info(f"Starting enrichment for {len(agencies)} agencies")
    
    # Create agent and task
    agent = create_enrichment_agent(llm)
    task = create_enrichment_task(agent, agencies)
    
    # Execute task
    try:
        result = agent.execute_task(task)
        
        # Count successful enrichments
        complete_count = sum(1 for a in result if a.get('enrichment_status') == 'complete')
        logger.info(f"Enrichment completed. {complete_count}/{len(agencies)} agencies successfully enriched")
        
        return result
    except Exception as e:
        logger.error(f"Error during enrichment: {e}")
        
        # Return agencies with incomplete status on error
        enriched_agencies = []
        for agency in agencies:
            enriched_agency = agency.copy()
            enriched_agency.update({
                'services': None,
                'niche': None,
                'notes': f"Enrichment failed: {str(e)}",
                'enrichment_status': 'incomplete'
            })
            enriched_agencies.append(enriched_agency)
        
        return enriched_agencies
