from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LeadRecord:
    """
    Core data structure for agency lead information.
    Flows through the pipeline and gets progressively enriched.
    """
    # Discovery phase
    agency_name: str
    website: str
    country: str
    
    # Enrichment phase
    services: Optional[str] = None
    niche: Optional[str] = None
    notes: Optional[str] = None
    enrichment_status: str = "pending"
    
    # Contact phase
    contact_name: Optional[str] = None
    email: Optional[str] = None
    contact_status: str = "pending"
    
    # Outreach phase
    outreach_message: Optional[str] = None
    message_length: Optional[int] = None
    
    # Scoring
    lead_score: str = field(default="Cold", init=False)
    
    def calculate_lead_score(self) -> str:
        """
        Calculate lead score based on data completeness.
        
        Hot: Contact information and enrichment data are complete
        Warm: Partial information is available (website and services)
        Cold: Minimal information or enrichment failed
        
        Returns:
            str: Lead score classification (Hot/Warm/Cold)
        """
        if self.email and self.enrichment_status == "complete":
            self.lead_score = "Hot"
        elif self.website and self.services:
            self.lead_score = "Warm"
        else:
            self.lead_score = "Cold"
        
        return self.lead_score
    
    def to_dict(self) -> dict:
        """
        Convert LeadRecord to dictionary for CSV export serialization.
        
        Returns:
            dict: Dictionary with all lead fields for export
        """
        return {
            "agency_name": self.agency_name,
            "country": self.country,
            "website": self.website,
            "services": self.services or "",
            "niche": self.niche or "",
            "contact_name": self.contact_name or "",
            "email": self.email or "",
            "lead_score": self.lead_score,
            "outreach_message": self.outreach_message or "",
        }
