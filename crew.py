"""
CrewAI Crew Configuration

This module defines the LeadGenCrew class that orchestrates all five agents
in a sequential pipeline: Finder → Enrichment → Contact → Outreach → Exporter
"""

import logging
from typing import List
from crewai import Crew, Agent, Task
from langchain_openai import ChatOpenAI

from agents.finder_agent import create_finder_agent, create_finder_task
from agents.enrichment_agent import create_enrichment_agent, create_enrichment_task
from agents.contact_agent import create_contact_agent, create_contact_task
from agents.outreach_agent import create_outreach_agent, create_outreach_task
from agents.exporter_agent import create_exporter_agent, create_exporter_task
from config import Config

logger = logging.getLogger(__name__)


class LeadGenCrew:
    """
    LeadGenCrew orchestrates the multi-agent pipeline for lead generation.
    
    The crew manages five specialized agents that work sequentially:
    1. Agency Finder - Discovers agencies in target country
    2. Enrichment Agent - Analyzes agency websites for business intelligence
    3. Contact Finder - Identifies decision-maker contact information
    4. Outreach Copywriter - Generates personalized cold email messages
    5. Exporter Agent - Saves all lead data to CSV
    """
    
    def __init__(self, config: Config):
        """
        Initialize the LeadGenCrew with configuration.
        
        Args:
            config: Configuration object with all system parameters
        """
        self.config = config
        self.llm = self._create_llm()
        self.agents = self._create_agents()
        self.tasks = self._create_tasks()
        
        logger.info("LeadGenCrew initialized with 5 agents")
    
    def _create_llm(self) -> ChatOpenAI:
        """
        Create and configure the LLM for all agents.
        
        Returns:
            ChatOpenAI: Configured language model instance
        """
        return ChatOpenAI(
            model=self.config.llm_model,
            api_key=self.config.openai_api_key,
            temperature=0.7
        )
    
    def _create_agents(self) -> List[Agent]:
        """
        Create all five agents with their configurations.
        
        Returns:
            List[Agent]: List of configured agents in execution order
        """
        logger.info("Creating agents...")
        
        agents = [
            create_finder_agent(self.llm),
            create_enrichment_agent(self.llm),
            create_contact_agent(self.llm),
            create_outreach_agent(self.llm),
            create_exporter_agent(
                self.llm,
                use_google_sheets=self.config.use_google_sheets,
                google_credentials_path=self.config.google_credentials_path
            )
        ]
        
        logger.info(f"Created {len(agents)} agents")
        return agents
    
    def _create_tasks(self) -> List[Task]:
        """
        Create tasks for the sequential pipeline.
        
        Tasks are configured with dependencies to ensure proper execution order:
        Finder → Enrichment → Contact → Outreach → Exporter
        
        Returns:
            List[Task]: List of configured tasks in execution order
        """
        logger.info("Creating tasks...")
        
        # Task 1: Agency Discovery
        finder_task = create_finder_task(
            agent=self.agents[0],
            target_country=self.config.target_country,
            target_count=self.config.target_count,
            search_query=self.config.search_query
        )
        
        # Task 2: Enrichment (depends on finder output)
        enrichment_task = create_enrichment_task(
            agent=self.agents[1],
            agencies=[]  # Will receive output from finder_task
        )
        enrichment_task.context = [finder_task]
        
        # Task 3: Contact Discovery (depends on enrichment output)
        contact_task = create_contact_task(
            agent=self.agents[2],
            agencies=[]  # Will receive output from enrichment_task
        )
        contact_task.context = [enrichment_task]
        
        # Task 4: Outreach Message Generation (depends on contact output)
        outreach_task = create_outreach_task(
            agent=self.agents[3],
            agencies=[]  # Will receive output from contact_task
        )
        outreach_task.context = [contact_task]
        
        # Task 5: Data Export (depends on outreach output)
        exporter_task = create_exporter_task(
            agent=self.agents[4],
            agencies=[],  # Will receive output from outreach_task
            output_path=self.config.output_file,
            use_google_sheets=self.config.use_google_sheets,
            google_sheet_id=self.config.google_sheet_id
        )
        exporter_task.context = [outreach_task]
        
        tasks = [
            finder_task,
            enrichment_task,
            contact_task,
            outreach_task,
            exporter_task
        ]
        
        logger.info(f"Created {len(tasks)} tasks with sequential dependencies")
        return tasks
    
    def get_crew(self) -> Crew:
        """
        Return configured CrewAI crew instance.
        
        The crew is configured for sequential task execution where each task
        receives the output from the previous task as context.
        
        Returns:
            Crew: Configured CrewAI crew ready for execution
        """
        crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process="sequential"  # Sequential execution: one task after another
        )
        
        logger.info("Crew configured and ready for execution")
        return crew
