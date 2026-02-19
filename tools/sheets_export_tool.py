import csv
import os
import logging
from pathlib import Path
from typing import List, Optional
from models import LeadRecord

logger = logging.getLogger(__name__)


class CSVExportTool:
    """
    Tool for exporting lead records to CSV files.
    Handles directory creation, proper CSV formatting, and escaping.
    """
    
    # CSV headers matching the export format from requirements
    CSV_HEADERS = [
        "agency_name",
        "country",
        "website",
        "services",
        "niche",
        "contact_name",
        "email",
        "lead_score",
        "outreach_message"
    ]
    
    def export_leads(self, leads: List[LeadRecord], output_path: str) -> None:
        """
        Export leads to CSV file with proper headers and escaping.
        Creates output directory if it doesn't exist.
        
        Args:
            leads: List of LeadRecord objects to export
            output_path: Path to the output CSV file
            
        Raises:
            IOError: If file cannot be written
            ValueError: If leads list is empty or invalid
        """
        if not leads:
            raise ValueError("Cannot export empty leads list")
        
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate lead scores before export
        for lead in leads:
            lead.calculate_lead_score()
        
        # Write CSV with proper escaping
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=self.CSV_HEADERS,
                quoting=csv.QUOTE_MINIMAL,
                escapechar='\\'
            )
            
            # Write headers
            writer.writeheader()
            
            # Write lead data
            for lead in leads:
                writer.writerow(lead.to_dict())
    
    def append_leads(self, leads: List[LeadRecord], output_path: str) -> None:
        """
        Append leads to existing CSV file.
        If file doesn't exist, creates new file with headers.
        
        Args:
            leads: List of LeadRecord objects to append
            output_path: Path to the output CSV file
            
        Raises:
            IOError: If file cannot be written
            ValueError: If leads list is empty or invalid
        """
        if not leads:
            raise ValueError("Cannot append empty leads list")
        
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate lead scores before export
        for lead in leads:
            lead.calculate_lead_score()
        
        # Check if file exists to determine if we need headers
        file_exists = output_file.exists() and output_file.stat().st_size > 0
        
        # Append to CSV with proper escaping
        with open(output_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=self.CSV_HEADERS,
                quoting=csv.QUOTE_MINIMAL,
                escapechar='\\'
            )
            
            # Write headers only if file is new or empty
            if not file_exists:
                writer.writeheader()
            
            # Write lead data
            for lead in leads:
                writer.writerow(lead.to_dict())



class GoogleSheetsExportTool:
    """
    Tool for exporting lead records to Google Sheets.
    Handles authentication with service account credentials and appending data to sheets.
    """
    
    # Sheet headers matching the export format
    SHEET_HEADERS = [
        "agency_name",
        "country",
        "website",
        "services",
        "niche",
        "contact_name",
        "email",
        "lead_score",
        "outreach_message"
    ]
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Google Sheets export tool with service account credentials.
        
        Args:
            credentials_path: Path to Google service account JSON credentials file.
                            If None, will look for GOOGLE_APPLICATION_CREDENTIALS env var.
        
        Raises:
            ImportError: If gspread or google-auth libraries are not installed
            FileNotFoundError: If credentials file is not found
            ValueError: If credentials are invalid
        """
        try:
            import gspread
            from google.oauth2.service_account import Credentials
        except ImportError:
            raise ImportError(
                "Google Sheets export requires 'gspread' and 'google-auth' packages. "
                "Install with: pip install gspread google-auth"
            )
        
        # Determine credentials path
        if credentials_path is None:
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not credentials_path:
            raise ValueError(
                "Google Sheets credentials not provided. Set GOOGLE_APPLICATION_CREDENTIALS "
                "environment variable or pass credentials_path parameter."
            )
        
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
        
        # Define required scopes for Google Sheets API
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        try:
            # Authenticate with service account
            credentials = Credentials.from_service_account_file(
                credentials_path,
                scopes=scopes
            )
            self.client = gspread.authorize(credentials)
            logger.info("Successfully authenticated with Google Sheets API")
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets: {e}")
            raise ValueError(f"Invalid Google Sheets credentials: {e}")
    
    def append_leads(self, leads: List[LeadRecord], sheet_id: str) -> None:
        """
        Append leads to Google Sheet.
        Creates headers if sheet is empty.
        
        Args:
            leads: List of LeadRecord objects to append
            sheet_id: Google Sheet ID (from the sheet URL)
            
        Raises:
            ValueError: If leads list is empty or sheet_id is invalid
            gspread.exceptions.APIError: If Google Sheets API request fails
        """
        if not leads:
            raise ValueError("Cannot append empty leads list")
        
        if not sheet_id:
            raise ValueError("Google Sheet ID is required")
        
        try:
            # Open the spreadsheet by ID
            spreadsheet = self.client.open_by_key(sheet_id)
            
            # Get the first worksheet (or create if doesn't exist)
            try:
                worksheet = spreadsheet.sheet1
            except Exception:
                worksheet = spreadsheet.add_worksheet(title="Leads", rows=1000, cols=len(self.SHEET_HEADERS))
            
            # Calculate lead scores before export
            for lead in leads:
                lead.calculate_lead_score()
            
            # Check if sheet is empty (needs headers)
            existing_data = worksheet.get_all_values()
            needs_headers = len(existing_data) == 0 or existing_data[0] != self.SHEET_HEADERS
            
            # Prepare data rows
            rows_to_append = []
            
            # Add headers if needed
            if needs_headers:
                rows_to_append.append(self.SHEET_HEADERS)
                logger.info("Adding headers to Google Sheet")
            
            # Convert leads to rows
            for lead in leads:
                lead_dict = lead.to_dict()
                row = [lead_dict.get(header, "") for header in self.SHEET_HEADERS]
                rows_to_append.append(row)
            
            # Append all rows at once for efficiency
            if rows_to_append:
                worksheet.append_rows(rows_to_append, value_input_option='USER_ENTERED')
                logger.info(f"Successfully appended {len(leads)} leads to Google Sheet {sheet_id}")
            
        except Exception as e:
            logger.error(f"Error appending leads to Google Sheet: {e}")
            raise
    
    def clear_sheet(self, sheet_id: str) -> None:
        """
        Clear all data from the Google Sheet.
        Useful for testing or resetting the sheet.
        
        Args:
            sheet_id: Google Sheet ID (from the sheet URL)
            
        Raises:
            ValueError: If sheet_id is invalid
            gspread.exceptions.APIError: If Google Sheets API request fails
        """
        if not sheet_id:
            raise ValueError("Google Sheet ID is required")
        
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.sheet1
            worksheet.clear()
            logger.info(f"Successfully cleared Google Sheet {sheet_id}")
        except Exception as e:
            logger.error(f"Error clearing Google Sheet: {e}")
            raise
