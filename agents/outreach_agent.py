"""
Outreach Copywriter Agent

This agent is responsible for generating personalized cold email messages for each agency.
It creates compelling, concise outreach messages (max 120 words) that include personalization
based on the agency's services and niche, with a clear call-to-action for a 15-minute call.
"""

import logging
from typing import List, Dict
from crewai import Agent, Task

logger = logging.getLogger(__name__)


def create_outreach_agent(llm) -> Agent:
    """
    Create the Outreach Copywriter agent.
    
    Args:
        llm: Language model instance for the agent
        
    Returns:
        Agent: Configured Outreach Copywriter agent
    """
    return Agent(
        role="Cold Email Copywriting Specialist",
        goal="Write personalized, compelling cold email messages that resonate with agency decision-makers and drive responses",
        backstory=(
            "You are a master of cold email copywriting with years of experience in B2B outreach. "
            "You understand what makes decision-makers at marketing agencies respond to emails. "
            "You know how to craft messages that are personal, concise, and value-driven without "
            "being pushy or salesy. Your specialty is writing emails that feel like they were "
            "written specifically for the recipient, referencing their business and showing genuine "
            "understanding of their work. You always keep messages under 120 words and include a "
            "clear, low-friction call-to-action. You understand that agency owners are busy and "
            "appreciate brevity and relevance."
        ),
        tools=[],  # No tools needed - uses LLM for message generation
        llm=llm,
        verbose=True,
        allow_delegation=False
    )


def create_outreach_task(agent: Agent, agencies: List[Dict]) -> Task:
    """
    Create the task for the Outreach Copywriter agent.
    
    Args:
        agent: The Outreach Copywriter agent
        agencies: List of agencies with enrichment and contact information
        
    Returns:
        Task: Configured task for outreach message generation
    """
    return Task(
        description=(
            f"Write personalized cold email outreach messages for the following agencies:\n\n"
            f"{agencies}\n\n"
            f"For each agency, create a compelling cold email message that:\n\n"
            f"REQUIREMENTS:\n"
            f"1. Maximum 120 words (strictly enforce this limit)\n"
            f"2. Includes a personalized opening line that references:\n"
            f"   - The agency's specific services (from the services field)\n"
            f"   - Their niche or specialization (from the niche field)\n"
            f"   - Something specific about their business\n"
            f"3. Presents a clear value proposition relevant to their agency\n"
            f"4. Includes a clear call-to-action requesting a 15-minute call\n"
            f"5. Uses a professional but conversational tone\n"
            f"6. Addresses the decision-maker by name if available (from contact_name field)\n\n"
            f"MESSAGE STRUCTURE:\n"
            f"- Opening: Personalized line referencing their agency/services/niche\n"
            f"- Value: Brief explanation of how you can help their agency\n"
            f"- CTA: Clear request for a 15-minute call\n"
            f"- Closing: Professional sign-off\n\n"
            f"TONE GUIDELINES:\n"
            f"- Be genuine and specific, not generic\n"
            f"- Show you've researched their agency\n"
            f"- Be confident but not pushy\n"
            f"- Focus on their needs, not your product\n"
            f"- Keep it conversational and human\n\n"
            f"WHAT TO AVOID:\n"
            f"- Generic templates that could apply to anyone\n"
            f"- Overly salesy or aggressive language\n"
            f"- Long paragraphs or complex sentences\n"
            f"- Multiple CTAs or confusing asks\n"
            f"- Exceeding the 120-word limit\n\n"
            f"Store the generated message in the outreach_message field and calculate the "
            f"message_length field (word count) for each agency."
        ),
        expected_output=(
            f"A list of agencies with personalized outreach messages in JSON format:\n"
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
            f'    "contact_status": "found",\n'
            f'    "outreach_message": "Hi John,\\n\\nI noticed [Agency Name] specializes in social media management for ecommerce brands. Many agencies like yours struggle with [specific pain point].\\n\\nWe help social media agencies [value proposition] so you can [benefit].\\n\\nWould you be open to a quick 15-minute call to explore how this could work for your team?\\n\\nBest,\\n[Your Name]",\n'
            f'    "message_length": 67\n'
            f"  }}\n"
            f"]\n"
            f"Each agency must include all previous fields plus outreach_message and message_length. "
            f"The outreach_message must be under 120 words and highly personalized."
        ),
        agent=agent
    )


def run_outreach_agent(agencies: List[Dict], llm) -> List[Dict]:
    """
    Execute the Outreach Copywriter agent to generate personalized messages.
    
    Args:
        agencies: List of agencies with enrichment and contact information
        llm: Language model instance
        
    Returns:
        List[Dict]: List of agencies with outreach messages added
    """
    logger.info(f"Starting outreach message generation for {len(agencies)} agencies")
    
    # Create agent and task
    agent = create_outreach_agent(llm)
    task = create_outreach_task(agent, agencies)
    
    # Execute task
    try:
        result = agent.execute_task(task)
        
        # Count successful message generations and check word counts
        messages_generated = sum(1 for a in result if a.get('outreach_message'))
        over_limit = sum(1 for a in result if a.get('message_length', 0) > 120)
        
        if over_limit > 0:
            logger.warning(f"{over_limit} messages exceeded the 120-word limit")
        
        logger.info(f"Outreach message generation completed. {messages_generated}/{len(agencies)} messages created")
        
        return result
    except Exception as e:
        logger.error(f"Error during outreach message generation: {e}")
        
        # Return agencies with empty outreach messages on error
        agencies_with_messages = []
        for agency in agencies:
            agency_with_message = agency.copy()
            agency_with_message.update({
                'outreach_message': '',
                'message_length': 0
            })
            agencies_with_messages.append(agency_with_message)
        
        return agencies_with_messages
