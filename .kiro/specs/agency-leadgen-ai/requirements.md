# Requirements Document

## Introduction

This document specifies the requirements for an agentic lead generation system designed to help B2B SaaS founders and lead generation service providers identify, enrich, and reach out to social media marketing agencies. The system automates the discovery of potential agency clients, enriches their profiles with relevant business information, identifies decision-makers, generates personalized outreach messages, and exports the data for further action.

## Glossary

- **LeadGen System**: The complete agentic lead generation application
- **Agency Finder**: The agent responsible for discovering marketing agencies
- **Enrichment Agent**: The agent that gathers additional business information about agencies
- **Contact Finder**: The agent that identifies decision-makers and their contact information
- **Outreach Copywriter**: The agent that generates personalized cold email messages
- **Exporter Agent**: The agent that saves lead data to CSV or Google Sheets
- **Lead Record**: A structured data entry containing agency information, contact details, and outreach message
- **Target Country**: The geographic market where agencies are being searched
- **Lead Score**: A classification (Hot/Warm/Cold) indicating lead quality
- **Outreach Message**: A personalized cold email draft for contacting an agency

## Requirements

### Requirement 1

**User Story:** As a B2B SaaS founder, I want to discover social media marketing agencies in specific countries, so that I can build a targeted list of potential clients

#### Acceptance Criteria

1. WHEN the user specifies a target country, THE Agency Finder SHALL retrieve at least 10 marketing agencies from that country
2. THE Agency Finder SHALL extract the agency name and website URL for each discovered agency
3. THE Agency Finder SHALL search data sources including Clutch.co, Sortlist, and Google Maps results
4. WHERE the user specifies a target count parameter, THE Agency Finder SHALL attempt to retrieve that number of agencies
5. THE LeadGen System SHALL store discovered agencies in a structured list format with name and website fields

### Requirement 2

**User Story:** As a lead generation specialist, I want to enrich agency profiles with business details, so that I can understand their services and target market

#### Acceptance Criteria

1. WHEN an agency is discovered, THE Enrichment Agent SHALL analyze the agency website to identify offered services
2. THE Enrichment Agent SHALL determine the agency niche such as ecommerce, local business, or B2B
3. THE Enrichment Agent SHALL extract company size signals from the website content
4. THE Enrichment Agent SHALL append enrichment data to the Lead Record including services, niche, and notes fields
5. IF the agency website is inaccessible, THEN THE Enrichment Agent SHALL mark the enrichment status as incomplete and continue processing

### Requirement 3

**User Story:** As a sales professional, I want to identify decision-makers at agencies with their contact information, so that I can reach the right person

#### Acceptance Criteria

1. WHEN agency enrichment is complete, THE Contact Finder SHALL search the agency website for contact page information
2. THE Contact Finder SHALL extract the name of a decision-maker such as CEO or Founder
3. THE Contact Finder SHALL extract the email address of the identified decision-maker when available
4. THE Contact Finder SHALL append contact_name and email fields to the Lead Record
5. IF no contact information is found, THEN THE Contact Finder SHALL leave the contact fields empty and mark the record as incomplete

### Requirement 4

**User Story:** As a sales professional, I want personalized outreach messages generated for each agency, so that I can send relevant cold emails efficiently

#### Acceptance Criteria

1. WHEN a Lead Record contains agency information, THE Outreach Copywriter SHALL generate a personalized cold email message
2. THE Outreach Copywriter SHALL limit the message length to a maximum of 120 words
3. THE Outreach Copywriter SHALL include a personalized line referencing the specific agency services or niche
4. THE Outreach Copywriter SHALL include a clear call-to-action requesting a 15-minute call
5. THE Outreach Copywriter SHALL store the generated message in the outreach_message field of the Lead Record

### Requirement 5

**User Story:** As a lead generation specialist, I want to export all lead data to CSV or Google Sheets, so that I can review and manage leads in my preferred tools

#### Acceptance Criteria

1. WHEN all agents complete processing, THE Exporter Agent SHALL compile all Lead Records into a structured format
2. THE Exporter Agent SHALL include the following fields in the export: agency_name, country, website, services, contact_name, email, lead_score, outreach_message
3. THE Exporter Agent SHALL save the data to a CSV file at the configured output path
4. WHERE Google Sheets export is configured, THE Exporter Agent SHALL append the lead data to the specified Google Sheet
5. THE Exporter Agent SHALL create the output directory if it does not exist

### Requirement 6

**User Story:** As a system administrator, I want to configure target parameters and output preferences, so that I can customize the lead generation process for different campaigns

#### Acceptance Criteria

1. THE LeadGen System SHALL read configuration parameters from a config.py file
2. THE LeadGen System SHALL support configuration of target_country, target_count, llm_model, and output_file parameters
3. THE LeadGen System SHALL support a send_emails boolean flag for future email automation
4. WHEN the user modifies configuration parameters, THE LeadGen System SHALL apply the new settings on the next execution
5. THE LeadGen System SHALL validate that required configuration parameters are present before execution

### Requirement 7

**User Story:** As a lead generation specialist, I want to run the system multiple times without duplicating leads, so that I can maintain a clean lead database

#### Acceptance Criteria

1. WHEN the LeadGen System executes, THE LeadGen System SHALL generate a log file with execution timestamp and summary
2. THE LeadGen System SHALL output a summary showing the number of agencies discovered, enriched, and exported
3. THE LeadGen System SHALL complete execution within a reasonable timeframe for the configured target_count
4. THE LeadGen System SHALL handle errors gracefully and continue processing remaining leads when individual agency processing fails
5. WHEN execution completes, THE LeadGen System SHALL display a summary of successful and failed lead processing attempts

### Requirement 8

**User Story:** As a B2B SaaS founder, I want the system to classify lead quality, so that I can prioritize my outreach efforts

#### Acceptance Criteria

1. WHEN a Lead Record is created, THE LeadGen System SHALL assign a lead_score classification of Hot, Warm, or Cold
2. THE LeadGen System SHALL classify a lead as Hot when contact information and enrichment data are complete
3. THE LeadGen System SHALL classify a lead as Warm when partial information is available
4. THE LeadGen System SHALL classify a lead as Cold when minimal information is available or enrichment failed
5. THE Exporter Agent SHALL include the lead_score field in all exported data
