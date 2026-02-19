"""
Agency Finder Agent

This agent is responsible for discovering marketing agencies in the target country.
It searches multiple sources (Clutch.co, Sortlist) and returns a structured list
of agencies with their name, website, and country.
"""

import logging
from typing import List, Dict
from crewai import Agent, Task
from tools.web_search_tool import WebSearchTool, WebScraperTool

logger = logging.getLogger(__name__)


def create_finder_agent(llm) -> Agent:
    """
    Create the Agency Finder agent.
    
    Args:
        llm: Language model instance for the agent
        
    Returns:
        Agent: Configured Agency Finder agent
    """
    return Agent(
        role="Marketing Agency Research Specialist",
        goal="Discover social media marketing agencies in the target country and extract their basic information",
        backstory=(
            "You are an expert at finding and researching marketing agencies across the globe. "
            "You have deep knowledge of agency directories like Clutch.co and Sortlist, and you know "
            "how to efficiently search for agencies that match specific criteria. Your specialty is "
            "discovering high-quality agencies and extracting accurate information about their online presence."
        ),
        tools=[WebSearchTool(), WebScraperTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )


def create_finder_task(agent: Agent, target_country: str, target_count: int, search_query: str) -> Task:
    """
    Create the task for the Agency Finder agent.
    
    Args:
        agent: The Agency Finder agent
        target_country: Country to search for agencies
        target_count: Number of agencies to discover
        search_query: Search query string
        
    Returns:
        Task: Configured task for agency discovery
    """
    return Task(
        description=(
            f"Search for {target_count} {search_query} agencies in {target_country}. "
            f"Use the Web Search Tool to discover agencies from multiple sources including "
            f"Clutch.co and Sortlist. For each agency found, extract:\n"
            f"1. Agency name\n"
            f"2. Website URL\n"
            f"3. Country\n\n"
            f"Focus on finding agencies that:\n"
            f"- Are actively operating in {target_country}\n"
            f"- Have a valid website URL\n"
            f"- Specialize in social media marketing\n\n"
            f"Return a structured list of agencies with all required information. "
            f"Ensure each agency has a valid name and website before including it in the results."
        ),
        expected_output=(
            f"A list of {target_count} agencies in JSON format with the following structure:\n"
            f"[\n"
            f"  {{\n"
            f'    "agency_name": "Agency Name",\n'
            f'    "website": "https://agency-website.com",\n'
            f'    "country": "{target_country}"\n'
            f"  }}\n"
            f"]\n"
            f"Each agency must have a valid name, website URL, and country field."
        ),
        agent=agent
    )


def run_finder_agent(target_country: str, target_count: int, search_query: str, llm) -> List[Dict]:
    """
    Execute the Agency Finder agent to discover agencies.
    
    Args:
        target_country: Country to search for agencies
        target_count: Number of agencies to discover
        search_query: Search query string
        llm: Language model instance
        
    Returns:
        List[Dict]: List of discovered agencies with name, website, and country
    """
    logger.info(f"Starting agency discovery for {target_country}")
    
    # Create agent and task
    agent = create_finder_agent(llm)
    task = create_finder_task(agent, target_country, target_count, search_query)
    
    # Execute task
    try:
        result = agent.execute_task(task)
        logger.info(f"Agency discovery completed. Found {len(result)} agencies")
        return result
    except Exception as e:
        logger.error(f"Error during agency discovery: {e}")
        raise
