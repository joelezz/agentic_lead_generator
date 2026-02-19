"""
Exporter Agent

This agent is responsible for compiling all Lead Records and exporting them to CSV
and optionally to Google Sheets. It calculates lead scores for each record and saves
the data to the configured output path(s).
"""

import logging
from typing import List, Dict, Optional
from crewai import Agent, Task
from tools.sheets_export_tool import CSVExportTool, GoogleSheetsExportTool
from models import LeadRecord

logger = logging.getLogger(__name__)


def create_exporter_agent(llm, use_google_sheets: bool = False, google_credentials_path: Optional[str] = None) -> Agent:
    """
    Create the Data Export Specialist agent.
    
    Args:
        llm: Language model instance for the agent
        use_google_sheets: Whether to enable Google Sheets export
        google_credentials_path: Path to Google service account credentials
        
    Returns:
        Agent: Configured Exporter agent
    """
    # Build tools list
    tools = [CSVExportTool()]
    
    # Add Google Sheets tool if configured
    if use_google_sheets:
        try:
            sheets_tool = GoogleSheetsExportTool(credentials_path=google_credentials_path)
            tools.append(sheets_tool)
        except Exception as e:
            logger.warning(f"Failed to initialize Google Sheets tool: {e}")
    
    return Agent(
        role="Data Export Specialist",
        goal="Save all lead data to CSV format and optionally to Google Sheets with proper formatting and lead score calculations",
        backstory=(
            "You are a meticulous data management specialist with expertise in data export "
            "and quality assurance. You understand the importance of clean, well-structured "
            "data exports for sales and marketing teams. Your role is to ensure that all "
            "lead information is properly compiled, scored, and saved in a format that's "
            "immediately usable for outreach campaigns. You take pride in delivering "
            "high-quality data exports with no missing fields or formatting issues. "
            "You always calculate lead scores accurately based on data completeness and "
            "ensure the output file is properly formatted for easy import into CRM systems, "
            "spreadsheet applications, or Google Sheets."
        ),
        tools=tools,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )


def create_exporter_task(
    agent: Agent, 
    agencies: List[Dict], 
    output_path: str,
    use_google_sheets: bool = False,
    google_sheet_id: Optional[str] = None
) -> Task:
    """
    Create the task for the Exporter agent.
    
    Args:
        agent: The Exporter agent
        agencies: List of agencies with all enrichment, contact, and outreach data
        output_path: Path to save the CSV file
        use_google_sheets: Whether to export to Google Sheets
        google_sheet_id: Google Sheet ID (if Google Sheets export is enabled)
        
    Returns:
        Task: Configured task for data export
    """
    google_sheets_instruction = ""
    if use_google_sheets and google_sheet_id:
        google_sheets_instruction = (
            f"\n\nGOOGLE SHEETS EXPORT:\n"
            f"- Also export the data to Google Sheets ID: {google_sheet_id}\n"
            f"- Use the GoogleSheetsExportTool to append leads to the sheet\n"
            f"- If Google Sheets export fails, log the error but continue with CSV export\n"
        )
    
    return Task(
        description=(
            f"Compile and export all lead data to CSV format at: {output_path}\n\n"
            f"Lead data to export:\n{agencies}\n\n"
            f"REQUIREMENTS:\n"
            f"1. Convert all agency data into LeadRecord objects\n"
            f"2. Calculate lead_score for each record using the calculate_lead_score() method:\n"
            f"   - Hot: email present AND enrichment_status is 'complete'\n"
            f"   - Warm: website present AND services present\n"
            f"   - Cold: minimal information or enrichment failed\n"
            f"3. Export all records to CSV with the following columns:\n"
            f"   - agency_name\n"
            f"   - country\n"
            f"   - website\n"
            f"   - services\n"
            f"   - niche\n"
            f"   - contact_name\n"
            f"   - email\n"
            f"   - lead_score\n"
            f"   - outreach_message\n"
            f"4. Ensure the output directory exists (create if needed)\n"
            f"5. Use proper CSV formatting with headers\n"
            f"6. Escape special characters in outreach messages properly\n"
            f"{google_sheets_instruction}\n"
            f"DATA QUALITY CHECKS:\n"
            f"- Verify all records have agency_name, website, and country\n"
            f"- Ensure lead_score is calculated for every record\n"
            f"- Handle missing optional fields gracefully (use empty strings)\n"
            f"- Validate that outreach_message content is properly escaped\n\n"
            f"Use the CSVExportTool to write the data to {output_path}."
        ),
        expected_output=(
            f"A CSV file saved at {output_path} containing all lead records with the following format:\n\n"
            f"agency_name,country,website,services,niche,contact_name,email,lead_score,outreach_message\n"
            f"Example Agency,Finland,https://example.com,Social Media Management,ecommerce,John Smith,john@example.com,Hot,\"Hi John...\"\n\n"
            f"Summary of export:\n"
            f"- Total leads exported: [count]\n"
            f"- Hot leads: [count]\n"
            f"- Warm leads: [count]\n"
            f"- Cold leads: [count]\n"
            f"- File location: {output_path}"
            f"{' and Google Sheets: ' + google_sheet_id if use_google_sheets else ''}"
        ),
        agent=agent
    )


def run_exporter_agent(
    agencies: List[Dict], 
    output_path: str, 
    llm,
    use_google_sheets: bool = False,
    google_sheet_id: Optional[str] = None,
    google_credentials_path: Optional[str] = None
) -> Dict:
    """
    Execute the Exporter agent to save leads to CSV and optionally to Google Sheets.
    
    Args:
        agencies: List of agencies with all data fields
        output_path: Path to save the CSV file
        llm: Language model instance
        use_google_sheets: Whether to export to Google Sheets
        google_sheet_id: Google Sheet ID (required if use_google_sheets is True)
        google_credentials_path: Path to Google credentials JSON file
        
    Returns:
        Dict: Export summary with counts and file location
    """
    logger.info(f"Starting data export for {len(agencies)} agencies to {output_path}")
    
    try:
        # Convert agencies to LeadRecord objects
        lead_records = []
        for agency in agencies:
            lead = LeadRecord(
                agency_name=agency.get('agency_name', ''),
                website=agency.get('website', ''),
                country=agency.get('country', ''),
                services=agency.get('services'),
                niche=agency.get('niche'),
                notes=agency.get('notes'),
                enrichment_status=agency.get('enrichment_status', 'pending'),
                contact_name=agency.get('contact_name'),
                email=agency.get('email'),
                contact_status=agency.get('contact_status', 'pending'),
                outreach_message=agency.get('outreach_message'),
                message_length=agency.get('message_length')
            )
            lead_records.append(lead)
        
        # Use CSVExportTool to export leads
        export_tool = CSVExportTool()
        export_tool.export_leads(lead_records, output_path)
        
        # Export to Google Sheets if configured
        google_sheets_status = "not_configured"
        if use_google_sheets:
            try:
                logger.info(f"Exporting to Google Sheets: {google_sheet_id}")
                sheets_tool = GoogleSheetsExportTool(credentials_path=google_credentials_path)
                sheets_tool.append_leads(lead_records, google_sheet_id)
                google_sheets_status = "success"
                logger.info("Successfully exported to Google Sheets")
            except Exception as e:
                logger.error(f"Failed to export to Google Sheets: {e}")
                google_sheets_status = f"failed: {str(e)}"
        
        # Calculate summary statistics
        hot_leads = sum(1 for lead in lead_records if lead.lead_score == "Hot")
        warm_leads = sum(1 for lead in lead_records if lead.lead_score == "Warm")
        cold_leads = sum(1 for lead in lead_records if lead.lead_score == "Cold")
        
        summary = {
            'total_leads': len(lead_records),
            'hot_leads': hot_leads,
            'warm_leads': warm_leads,
            'cold_leads': cold_leads,
            'file_location': output_path,
            'google_sheets_status': google_sheets_status,
            'google_sheet_id': google_sheet_id if use_google_sheets else None,
            'status': 'success'
        }
        
        logger.info(
            f"Export completed successfully: {len(lead_records)} leads exported "
            f"(Hot: {hot_leads}, Warm: {warm_leads}, Cold: {cold_leads})"
        )
        
        return summary
        
    except Exception as e:
        logger.error(f"Error during data export: {e}")
        return {
            'total_leads': 0,
            'hot_leads': 0,
            'warm_leads': 0,
            'cold_leads': 0,
            'file_location': output_path,
            'google_sheets_status': 'not_attempted',
            'google_sheet_id': None,
            'status': 'failed',
            'error': str(e)
        }
