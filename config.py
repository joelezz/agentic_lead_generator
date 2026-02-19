"""
Configuration module for Agency LeadGen AI system.

This module defines the configuration dataclass and handles loading
configuration from environment variables with validation.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration dataclass for all system parameters."""
    
    # LLM settings
    llm_model: str = "gpt-4o-mini"
    openai_api_key: str = ""
    
    # Search parameters
    target_country: str = "Finland"
    target_count: int = 20
    search_query: str = "social media marketing agency"
    
    # Output settings
    output_file: str = "outputs/leads.csv"
    log_file: str = "outputs/logs.txt"
    
    # Google Sheets (optional)
    use_google_sheets: bool = False
    google_sheet_id: Optional[str] = None
    google_credentials_path: Optional[str] = None
    
    # Future features
    send_emails: bool = False
    
    @classmethod
    def from_env(cls) -> "Config":
        """
        Load configuration from environment variables.
        
        Returns:
            Config: Configuration instance with values from environment
        """
        load_dotenv()
        
        return cls(
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            target_country=os.getenv("TARGET_COUNTRY", "Finland"),
            target_count=int(os.getenv("TARGET_COUNT", "20")),
            search_query=os.getenv("SEARCH_QUERY", "social media marketing agency"),
            output_file=os.getenv("OUTPUT_FILE", "outputs/leads.csv"),
            log_file=os.getenv("LOG_FILE", "outputs/logs.txt"),
            use_google_sheets=os.getenv("USE_GOOGLE_SHEETS", "false").lower() == "true",
            google_sheet_id=os.getenv("GOOGLE_SHEET_ID"),
            google_credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            send_emails=os.getenv("SEND_EMAILS", "false").lower() == "true",
        )
    
    def validate(self) -> None:
        """
        Validate that required configuration parameters are present.
        
        Raises:
            ValueError: If required parameters are missing or invalid
        """
        errors = []
        
        # Validate required parameters
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required but not set")
        
        if not self.target_country:
            errors.append("TARGET_COUNTRY cannot be empty")
        
        if self.target_count <= 0:
            errors.append(f"TARGET_COUNT must be positive, got {self.target_count}")
        
        if not self.search_query:
            errors.append("SEARCH_QUERY cannot be empty")
        
        if not self.output_file:
            errors.append("OUTPUT_FILE cannot be empty")
        
        if not self.log_file:
            errors.append("LOG_FILE cannot be empty")
        
        # Validate Google Sheets configuration if enabled
        if self.use_google_sheets:
            if not self.google_sheet_id:
                errors.append("GOOGLE_SHEET_ID is required when USE_GOOGLE_SHEETS is true")
            if not self.google_credentials_path:
                errors.append("GOOGLE_APPLICATION_CREDENTIALS is required when USE_GOOGLE_SHEETS is true")
        
        # Raise all validation errors together
        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_message)
    
    def __str__(self) -> str:
        """Return string representation with masked API key."""
        masked_key = f"{self.openai_api_key[:8]}..." if self.openai_api_key else "NOT SET"
        return (
            f"Config(\n"
            f"  llm_model={self.llm_model}\n"
            f"  openai_api_key={masked_key}\n"
            f"  target_country={self.target_country}\n"
            f"  target_count={self.target_count}\n"
            f"  search_query={self.search_query}\n"
            f"  output_file={self.output_file}\n"
            f"  log_file={self.log_file}\n"
            f"  use_google_sheets={self.use_google_sheets}\n"
            f"  google_sheet_id={self.google_sheet_id}\n"
            f"  google_credentials_path={self.google_credentials_path}\n"
            f"  send_emails={self.send_emails}\n"
            f")"
        )


def load_config() -> Config:
    """
    Load and validate configuration.
    
    Returns:
        Config: Validated configuration instance
        
    Raises:
        ValueError: If configuration validation fails
    """
    config = Config.from_env()
    config.validate()
    return config
