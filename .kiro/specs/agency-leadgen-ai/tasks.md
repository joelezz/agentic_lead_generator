# Implementation Plan

- [x] 1. Set up project structure and dependencies
  - Create directory structure: agents/, tools/, outputs/
  - Create requirements.txt with CrewAI, OpenAI, BeautifulSoup4, requests, gspread, python-dotenv, tenacity
  - Create .env.example file with required environment variables
  - Create .gitignore to exclude .env, outputs/, and __pycache__
  - _Requirements: 6.1, 6.5_

- [x] 2. Implement configuration system
  - Create config.py with Config dataclass for all system parameters
  - Implement environment variable loading for OpenAI API key
  - Add configuration validation to ensure required parameters are present
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 3. Implement core data models
  - Create models.py with LeadRecord dataclass
  - Implement calculate_lead_score() method with Hot/Warm/Cold logic
  - Add to_dict() method for CSV export serialization
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 4. Implement web scraping tools
  - Create tools/web_search_tool.py with WebSearchTool and WebScraperTool classes
  - Implement scrape_website() method with BeautifulSoup4 for content extraction
  - Implement extract_contact_page() method to find contact page URLs
  - Add retry logic with tenacity for network resilience
  - Add rate limiting delays (1-2 seconds between requests)
  - _Requirements: 1.2, 1.3, 2.1, 3.1_

- [x] 5. Implement email extraction tool
  - Create tools/email_finder_tool.py with EmailExtractorTool class
  - Implement extract_emails() method using regex patterns
  - Implement find_decision_maker_email() to identify CEO/Founder emails
  - _Requirements: 3.2, 3.3, 3.4_

- [x] 6. Implement CSV export tool
  - Create tools/sheets_export_tool.py with CSVExportTool class
  - Implement export_leads() method to write CSV with proper headers
  - Ensure output directory creation if it doesn't exist
  - Add proper CSV escaping for message content
  - _Requirements: 5.1, 5.2, 5.3, 5.5_

- [x] 7. Implement Agency Finder agent
  - Create agents/finder_agent.py with agent configuration
  - Define agent role as "Marketing Agency Research Specialist"
  - Create agent goal to discover agencies in target country
  - Implement task to search and extract agency name and website
  - Use WebSearchTool and WebScraperTool
  - Return structured list of agencies with name, website, country
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 8. Implement Enrichment agent
  - Create agents/enrichment_agent.py with agent configuration
  - Define agent role as "Business Intelligence Analyst"
  - Create agent goal to analyze agency websites for services and niche
  - Implement task to scrape and analyze website content
  - Extract services, niche, and company size signals
  - Handle inaccessible websites by marking enrichment_status as incomplete
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 9. Implement Contact Finder agent
  - Create agents/contact_agent.py with agent configuration
  - Define agent role as "Contact Research Specialist"
  - Create agent goal to find decision-maker contact information
  - Implement task to search contact pages and extract names and emails
  - Use WebScraperTool and EmailExtractorTool
  - Handle missing contact info by leaving fields empty
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 10. Implement Outreach Copywriter agent
  - Create agents/outreach_agent.py with agent configuration
  - Define agent role as "Cold Email Copywriting Specialist"
  - Create agent goal to write personalized outreach messages
  - Implement task with prompt template for 120-word max emails
  - Include personalization based on agency services/niche
  - Add clear CTA for 15-minute call
  - Store message in outreach_message field
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 11. Implement Exporter agent
  - Create agents/exporter_agent.py with agent configuration
  - Define agent role as "Data Export Specialist"
  - Create agent goal to save leads to CSV
  - Implement task to compile all Lead Records and export
  - Use CSVExportTool to write to configured output path
  - Calculate and include lead_score for each record
  - _Requirements: 5.1, 5.2, 5.3, 5.5, 8.5_

- [x] 12. Implement CrewAI crew configuration
  - Create crew.py with LeadGenCrew class
  - Implement _create_agents() to instantiate all five agents
  - Implement _create_tasks() to define sequential task pipeline
  - Configure task dependencies: Finder → Enrichment → Contact → Outreach → Exporter
  - Set up LLM configuration for all agents using GPT-4o-mini
  - Implement get_crew() to return configured Crew instance
  - _Requirements: 1.5, 2.4, 3.4, 4.5, 5.1_

- [x] 13. Implement main orchestrator
  - Create main.py as entry point
  - Load configuration from config.py and environment variables
  - Initialize LeadGenCrew with configuration
  - Execute crew.kickoff() to run the pipeline
  - Capture and display execution results
  - Print summary with counts of discovered, enriched, and exported leads
  - _Requirements: 6.4, 7.2, 7.3_

- [x] 14. Implement error handling and logging
  - Set up logging configuration in main.py
  - Configure file handler for outputs/logs.txt
  - Configure console handler for real-time feedback
  - Add try-except blocks in all tools for network and parsing errors
  - Implement "continue on error" logic in agent tasks
  - Log errors with context (URL, agency name, error type)
  - _Requirements: 2.5, 3.5, 7.1, 7.4, 7.5_

- [x] 15. Create project documentation
  - Create README.md with project overview and setup instructions
  - Document required environment variables
  - Add usage examples with different configurations
  - Document output CSV format
  - Include troubleshooting section for common issues
  - _Requirements: 6.1, 6.2, 6.3_

- [x] 16. Implement Google Sheets export (optional)
  - Create GoogleSheetsExportTool class in tools/sheets_export_tool.py
  - Implement authentication with service account credentials
  - Implement append_leads() method to write to Google Sheets
  - Add use_google_sheets and google_sheet_id to config
  - Update Exporter agent to conditionally use Google Sheets
  - _Requirements: 5.4_
