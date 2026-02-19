<<<<<<< HEAD
# agentic_lead_generator
=======
# Agency LeadGen AI

An intelligent, multi-agent lead generation system that automates the discovery, enrichment, and outreach preparation for social media marketing agencies. Built with CrewAI and powered by OpenAI's GPT-4o-mini.

## Overview

Agency LeadGen AI orchestrates five specialized AI agents in a sequential pipeline to:

1. **Discover** marketing agencies in target countries
2. **Enrich** agency profiles with business intelligence
3. **Find** decision-maker contact information
4. **Generate** personalized outreach messages
5. **Export** qualified leads to CSV or Google Sheets

Perfect for B2B SaaS founders, lead generation specialists, and sales professionals looking to build targeted agency prospect lists.

## Features

- 🤖 **Multi-Agent Pipeline**: Five specialized agents working in sequence
- 🌍 **Geographic Targeting**: Search agencies by country
- 📊 **Lead Scoring**: Automatic Hot/Warm/Cold classification
- ✉️ **Personalized Outreach**: AI-generated cold emails (max 120 words)
- 📁 **Flexible Export**: CSV files or Google Sheets integration
- 🔄 **Error Resilient**: Continues processing even if individual leads fail
- 📝 **Detailed Logging**: Comprehensive execution logs for debugging

## Architecture

```
User Config → Agency Finder → Enrichment Agent → Contact Finder → Outreach Copywriter → Exporter Agent → CSV/Sheets
```

Each agent specializes in a specific task and passes enriched data to the next agent in the pipeline.

## Requirements

- Python 3.10 or higher
- OpenAI API key
- Internet connection for web scraping

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd agency-leadgen-ai
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and add your API key:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Configuration

### Required Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | - | ✅ Yes |

### Optional Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LLM_MODEL` | OpenAI model to use | `gpt-4o-mini` | No |
| `TARGET_COUNTRY` | Country to search for agencies | `Finland` | No |
| `TARGET_COUNT` | Number of agencies to discover | `20` | No |
| `SEARCH_QUERY` | Search query for agencies | `social media marketing agency` | No |
| `OUTPUT_FILE` | Path to output CSV file | `outputs/leads.csv` | No |
| `LOG_FILE` | Path to log file | `outputs/logs.txt` | No |
| `USE_GOOGLE_SHEETS` | Enable Google Sheets export | `false` | No |
| `GOOGLE_SHEET_ID` | Google Sheet ID (if enabled) | - | Only if `USE_GOOGLE_SHEETS=true` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Google service account JSON | - | Only if `USE_GOOGLE_SHEETS=true` |
| `SEND_EMAILS` | Enable email sending (future) | `false` | No |

### Google Sheets Integration (Optional)

To export leads directly to Google Sheets:

#### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API and Google Drive API

#### 2. Create Service Account Credentials

1. Navigate to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Give it a name (e.g., "leadgen-exporter")
4. Click "Create and Continue"
5. Skip role assignment (click "Continue")
6. Click "Done"

#### 3. Generate JSON Key

1. Click on the created service account
2. Go to "Keys" tab
3. Click "Add Key" > "Create new key"
4. Select "JSON" format
5. Download the JSON file
6. Save it securely (e.g., `credentials/google-service-account.json`)

#### 4. Share Google Sheet with Service Account

1. Create a new Google Sheet or open an existing one
2. Copy the Sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit
   ```
3. Click "Share" button
4. Add the service account email (found in the JSON file as `client_email`)
5. Give it "Editor" permissions

#### 5. Configure Environment Variables

Add to your `.env` file:

```env
USE_GOOGLE_SHEETS=true
GOOGLE_SHEET_ID=your_sheet_id_here
GOOGLE_APPLICATION_CREDENTIALS=credentials/google-service-account.json
```

#### 6. Run with Google Sheets Export

```bash
python main.py
```

Leads will be exported to both CSV and Google Sheets automatically.

### Configuration in Code

You can also modify `config.py` directly to change default values:

```python
@dataclass
class Config:
    llm_model: str = "gpt-4o-mini"
    target_country: str = "Finland"
    target_count: int = 20
    search_query: str = "social media marketing agency"
    output_file: str = "outputs/leads.csv"
    log_file: str = "outputs/logs.txt"
    use_google_sheets: bool = False
    google_sheet_id: Optional[str] = None
    google_credentials_path: Optional[str] = None
    # ... other settings
```

## Usage

### Basic Usage

Run the system with default settings (20 agencies in Finland):

```bash
python main.py
```

### Custom Target Country

Search for agencies in a different country:

```bash
TARGET_COUNTRY="Germany" python main.py
```

### Custom Target Count

Discover more or fewer agencies:

```bash
TARGET_COUNT=50 python main.py
```

### Multiple Configuration Options

Combine multiple settings:

```bash
TARGET_COUNTRY="United Kingdom" TARGET_COUNT=30 SEARCH_QUERY="digital marketing agency" python main.py
```

### Using Environment File

Set all configurations in `.env`:

```env
OPENAI_API_KEY=sk-...
TARGET_COUNTRY=Spain
TARGET_COUNT=25
SEARCH_QUERY=social media agency
OUTPUT_FILE=outputs/spain_agencies.csv
```

Then run:

```bash
python main.py
```

## Output Format

### CSV File Structure

The system exports leads to a CSV file with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `agency_name` | Name of the agency | "Digital Boost Agency" |
| `country` | Target country | "Finland" |
| `website` | Agency website URL | "https://digitalboost.fi" |
| `services` | Services offered | "Social media management, content creation" |
| `niche` | Target market niche | "E-commerce brands" |
| `contact_name` | Decision-maker name | "John Smith" |
| `email` | Contact email address | "john@digitalboost.fi" |
| `lead_score` | Quality classification | "Hot", "Warm", or "Cold" |
| `outreach_message` | Personalized email | "Hi John, I noticed..." |

### Lead Scoring System

- **Hot**: Complete contact information + full enrichment data
- **Warm**: Partial information (website + services)
- **Cold**: Minimal information or enrichment failed

### Example Output

```csv
agency_name,country,website,services,niche,contact_name,email,lead_score,outreach_message
Digital Boost Agency,Finland,https://digitalboost.fi,"Social media management, content creation",E-commerce brands,John Smith,john@digitalboost.fi,Hot,"Hi John, I noticed Digital Boost specializes in e-commerce social media..."
```

## Project Structure

```
agency-leadgen-ai/
├── agents/                      # Agent definitions
│   ├── finder_agent.py         # Agency discovery
│   ├── enrichment_agent.py     # Business intelligence
│   ├── contact_agent.py        # Contact finding
│   ├── outreach_agent.py       # Message generation
│   └── exporter_agent.py       # Data export
├── tools/                       # Agent tools
│   ├── web_search_tool.py      # Web scraping utilities
│   ├── email_finder_tool.py    # Email extraction
│   └── sheets_export_tool.py   # CSV/Sheets export
├── outputs/                     # Generated files
│   ├── leads.csv               # Exported leads
│   └── logs.txt                # Execution logs
├── .kiro/                       # Spec documentation
│   └── specs/agency-leadgen-ai/
│       ├── requirements.md     # System requirements
│       ├── design.md           # Architecture design
│       └── tasks.md            # Implementation tasks
├── config.py                    # Configuration management
├── crew.py                      # CrewAI orchestration
├── main.py                      # Entry point
├── models.py                    # Data models
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── README.md                    # This file
```

## How It Works

### Agent Pipeline

1. **Agency Finder Agent**
   - Searches Clutch.co, Sortlist, and Google Maps
   - Extracts agency names and websites
   - Creates initial Lead Records

2. **Enrichment Agent**
   - Scrapes agency websites
   - Identifies services and niche
   - Adds business intelligence to leads

3. **Contact Finder Agent**
   - Locates contact pages
   - Extracts decision-maker names
   - Finds email addresses

4. **Outreach Copywriter Agent**
   - Generates personalized cold emails
   - References specific agency details
   - Includes clear call-to-action

5. **Exporter Agent**
   - Calculates lead scores
   - Exports to CSV or Google Sheets
   - Generates execution summary

### Data Flow

```python
# Initial Discovery
LeadRecord(
    agency_name="Digital Boost",
    website="https://digitalboost.fi",
    country="Finland"
)

# After Enrichment
LeadRecord(
    ...previous_fields,
    services="Social media management",
    niche="E-commerce",
    enrichment_status="complete"
)

# After Contact Finding
LeadRecord(
    ...previous_fields,
    contact_name="John Smith",
    email="john@digitalboost.fi",
    contact_status="found"
)

# After Outreach Generation
LeadRecord(
    ...previous_fields,
    outreach_message="Hi John, I noticed...",
    lead_score="Hot"
)
```

## Troubleshooting

### Common Issues

#### 1. Missing OpenAI API Key

**Error:**
```
Configuration Error:
  - OPENAI_API_KEY is required but not set
```

**Solution:**
- Ensure `.env` file exists in the project root
- Add your OpenAI API key: `OPENAI_API_KEY=sk-...`
- Verify the key is valid at https://platform.openai.com/api-keys

#### 2. Import Errors / Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'crewai'
```

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 3. Rate Limiting / API Errors

**Error:**
```
openai.error.RateLimitError: Rate limit exceeded
```

**Solution:**
- Reduce `TARGET_COUNT` to process fewer agencies
- Wait a few minutes before retrying
- Check your OpenAI API usage limits
- Consider upgrading your OpenAI plan

#### 4. Web Scraping Failures

**Error:**
```
Failed to scrape website: Connection timeout
```

**Solution:**
- Check your internet connection
- Some websites may block automated scraping
- The system will continue with other leads (error resilient)
- Check `outputs/logs.txt` for detailed error information

#### 5. Empty or Incomplete Results

**Issue:** CSV file has many leads with missing data

**Solution:**
- This is normal - not all websites have accessible contact info
- Focus on "Hot" and "Warm" leads with complete data
- Increase `TARGET_COUNT` to get more complete leads
- Check `outputs/logs.txt` to see which agencies failed enrichment

#### 6. Permission Errors

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'outputs/leads.csv'
```

**Solution:**
- Close the CSV file if it's open in Excel/Sheets
- Ensure the `outputs/` directory is writable
- Run with appropriate file permissions

#### 7. Google Sheets Integration Issues

**Error:**
```
Configuration validation failed:
  - GOOGLE_SHEET_ID is required when USE_GOOGLE_SHEETS is true
```

**Solution:**
- Set `GOOGLE_SHEET_ID` in `.env` file
- Ensure Google Sheets credentials are configured
- Or set `USE_GOOGLE_SHEETS=false` to use CSV only

### Debugging Tips

1. **Check Logs**: Always review `outputs/logs.txt` for detailed error messages
2. **Start Small**: Test with `TARGET_COUNT=5` before running larger batches
3. **Verify Config**: Run with verbose output to see configuration values
4. **Test Connectivity**: Ensure you can access target websites manually
5. **API Limits**: Monitor your OpenAI API usage dashboard

### Getting Help

If you encounter issues not covered here:

1. Check the logs in `outputs/logs.txt`
2. Review the requirements in `.kiro/specs/agency-leadgen-ai/requirements.md`
3. Consult the design document in `.kiro/specs/agency-leadgen-ai/design.md`
4. Open an issue with:
   - Error message
   - Configuration used
   - Relevant log excerpts
   - Steps to reproduce

## Performance Considerations

- **Execution Time**: Expect 2-5 minutes per agency (web scraping + AI processing)
- **API Costs**: ~$0.10-0.30 per 20 agencies (varies by model and content)
- **Rate Limiting**: Built-in delays (1-2 seconds) between requests
- **Memory Usage**: Minimal - processes leads sequentially

## Limitations

- Web scraping depends on website structure and accessibility
- Some agencies may not have public contact information
- Email extraction relies on emails being visible on websites
- Rate limits apply to both OpenAI API and web scraping
- Google Sheets integration requires additional setup (optional)

## Future Enhancements

- ✉️ Automated email sending via SendGrid
- 🔄 Lead deduplication across runs
- 🔗 CRM integration (HubSpot, Salesforce)
- ⏰ Scheduled automated runs
- 🌐 Multi-language support
- 📊 Analytics dashboard

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

For questions or support, please [add contact information or issue tracker link].

---

**Built with ❤️ using CrewAI and OpenAI**
>>>>>>> 9d05b87 (First commit)
