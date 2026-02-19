"""
Agency LeadGen AI - Main Orchestrator

Entry point for the agentic lead generation system that discovers,
enriches, and prepares outreach for social media marketing agencies.
"""

import logging
import sys
import os
from datetime import datetime

from config import load_config
from crew import LeadGenCrew


def setup_logging(log_file: str) -> None:
    """
    Configure logging for both file and console output.
    
    Args:
        log_file: Path to the log file
    """
    # Create outputs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def print_banner():
    """Print application banner."""
    print("\n" + "="*60)
    print("  Agency LeadGen AI - Agentic Lead Generation System")
    print("="*60 + "\n")


def print_summary(result, config, start_time: datetime, end_time: datetime):
    """
    Print execution summary with counts and statistics.
    
    Args:
        result: Crew execution result
        config: Configuration object
        start_time: Execution start timestamp
        end_time: Execution end timestamp
    """
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*60)
    print("  EXECUTION SUMMARY")
    print("="*60)
    print(f"\nTarget Country: {config.target_country}")
    print(f"Target Count: {config.target_count}")
    print(f"Search Query: {config.search_query}")
    print(f"\nExecution Time: {duration:.2f} seconds")
    print(f"Output File: {config.output_file}")
    print(f"Log File: {config.log_file}")
    
    # Parse result to extract counts if available
    # Note: The actual result format depends on CrewAI's output
    print(f"\nStatus: Completed")
    print("\nPipeline executed successfully!")
    print("Check the output file for discovered and enriched leads.")
    print("\n" + "="*60 + "\n")


def main():
    """
    Main orchestrator function.
    
    Loads configuration, initializes the CrewAI crew, executes the pipeline,
    and displays execution results.
    """
    try:
        # Print banner
        print_banner()
        
        # Load and validate configuration
        print("Loading configuration...")
        config = load_config()
        print(f"Configuration loaded successfully")
        print(f"  Target: {config.target_count} agencies in {config.target_country}")
        print(f"  Model: {config.llm_model}")
        print(f"  Output: {config.output_file}\n")
        
        # Setup logging
        setup_logging(config.log_file)
        logger = logging.getLogger(__name__)
        logger.info("="*60)
        logger.info("Starting Agency LeadGen AI execution")
        logger.info(f"Configuration: {config}")
        logger.info("="*60)
        
        # Initialize LeadGenCrew
        print("Initializing LeadGen Crew...")
        crew_manager = LeadGenCrew(config)
        crew = crew_manager.get_crew()
        print("Crew initialized with 5 agents\n")
        
        # Execute the pipeline
        print("Starting pipeline execution...")
        print("This may take several minutes depending on target count...\n")
        logger.info("Executing crew.kickoff()")
        
        start_time = datetime.now()
        result = crew.kickoff()
        end_time = datetime.now()
        
        logger.info("Crew execution completed")
        logger.info(f"Result: {result}")
        
        # Display summary
        print_summary(result, config, start_time, end_time)
        
        logger.info("="*60)
        logger.info("Agency LeadGen AI execution completed successfully")
        logger.info("="*60)
        
        return 0
        
    except ValueError as e:
        # Configuration validation errors
        print(f"\n❌ Configuration Error:\n{e}\n")
        logging.error(f"Configuration validation failed: {e}")
        return 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Execution interrupted by user\n")
        logging.warning("Execution interrupted by user")
        return 130
        
    except Exception as e:
        # Unexpected errors
        print(f"\n❌ Unexpected Error:\n{e}\n")
        logging.exception("Unexpected error during execution")
        return 1


if __name__ == "__main__":
    sys.exit(main())
