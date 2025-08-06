# AI Agents for Asana Workflow Automation

This repository contains two AI agents built with the Agno framework for automating workflows:

1. **Asana Form Agent** - Automates USAC Form 471/470 processing workflow
2. **Finance Agent** - Provides comprehensive financial market analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- Asana API key (for Asana agent)

### Installation

1. **Clone and setup environment:**
```bash
git clone <repository-url>
cd agents
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment variables:**
```bash
cp example.env .env
# Edit .env with your API keys
```

3. **Required environment variables:**
```bash
OPENAI_API_KEY=your_openai_api_key
ASANA_API_KEY=your_asana_api_key          # For Asana agent
ASANA_PROJECT_ID=your_project_id          # For Asana agent
TEMP_DOWNLOAD_DIR=/tmp/agno_pdfs         # For Asana agent
```

## 🤖 Agents

### 1. Asana Form Agent (`asana_form_agent.py`)

**Purpose:** Automates USAC Form 471/470 processing workflow in Asana

**Features:**
- Monitors "QA" section for new tasks
- Downloads and processes PDF attachments/URLs
- Extracts form information (application number, entity name)
- Searches USAC API for matching Form 470 documents
- Moves tasks between sections based on results:
  - "QA – Processing" → "QA – Manual Follow-up Required" (if Form 470 not found)
  - "QA – Processing" → Task completed (if Form 470 found)
  - "QA – Processing" → "QA - Issues" (if PDF download fails)

**Usage:**
```bash
# Run once
python3 asana_form_agent.py

# Run in watcher mode (checks every 60 seconds)
python3 asana_form_agent.py --watcher
```

**Workflow:**
1. **Monitor QA Section** - Gets all tasks in QA section
2. **Move to Processing** - Moves tasks to "QA – Processing" section
3. **PDF Processing** - Downloads PDFs and extracts form information
4. **Form 470 Search** - Searches USAC API for matching documents
5. **Workflow Decisions** - Moves tasks to appropriate sections based on results

### 2. Finance Agent (`finance_agent.py`)

**Purpose:** Provides comprehensive financial market analysis using Yahoo Finance data

**Features:**
- Real-time stock price data
- Financial metrics (P/E, Market Cap, EPS)
- Analyst recommendations
- Company news and information
- Historical price analysis
- Industry comparisons

**Usage:**
```bash
python3 finance_agent.py
```

**Example queries:**
- "What's the latest news and financial performance of Apple (AAPL)?"
- "Analyze the semiconductor market performance focusing on NVIDIA, AMD, Intel, and TSMC"
- "Evaluate the automotive industry's current state including Tesla, Ford, GM, and Toyota"

## 📁 Project Structure

```
agents/
├── asana_form_agent.py    # Main Asana workflow automation agent
├── finance_agent.py       # Financial market analysis agent
├── add_qa_task.py        # Script to add test tasks to QA section
├── requirements.txt       # Python dependencies
├── example.env           # Environment variables template
└── README.md            # This documentation
```

## 🛠️ Tools and Dependencies

### Asana Form Agent Tools:
- **Asana API** - Task management, section movement, comments
- **PDF Processing** - PyPDF2, pdfplumber for text extraction
- **USAC API** - Form 470 search and retrieval
- **File Management** - Temporary PDF storage and cleanup

### Finance Agent Tools:
- **YFinance** - Real-time financial data
- **OpenAI GPT-4** - Natural language processing and analysis

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```bash
# Required for both agents
OPENAI_API_KEY=your_openai_api_key_here

# Required for Asana Form Agent
ASANA_API_KEY=your_asana_api_key_here
ASANA_PROJECT_ID=your_asana_project_id_here
TEMP_DOWNLOAD_DIR=/tmp/agno_pdfs

# Optional
ASANA_QA_STATUS=QA
```

### Asana Project Setup

Your Asana project should have these sections:
- **QA** - Initial tasks to be processed
- **QA – Processing** - Tasks currently being processed
- **QA – Manual Follow-up Required** - Tasks requiring manual review
- **QA - Issues** - Tasks with technical issues

## 🚀 Production Deployment

### Running in Production

1. **Set up environment:**
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp example.env .env
# Edit .env with production values
```

2. **Run Asana agent in watcher mode:**
```bash
python3 asana_form_agent.py --watcher
```

3. **Add test tasks:**
```bash
python3 add_qa_task.py
```

### Monitoring and Logging

The agents provide detailed step-by-step logging:
- Tool call results
- API responses
- Workflow transitions
- Error handling

### Error Handling

- **API Failures** - Graceful degradation with fallback options
- **PDF Processing** - Handles corrupted or invalid PDFs
- **Section Movement** - Fallback to comments if API limitations
- **Network Issues** - Retry logic for external API calls

## 🔍 Testing

### Adding Test Tasks

Use the included script to add test tasks:

```bash
python3 add_qa_task.py
```

This creates tasks with different scenarios:
- Form 471 with PDF URL
- No PDF available
- Invalid PDF URL

### Testing the Workflow

1. Add test tasks to QA section
2. Run the agent in watcher mode
3. Monitor task movements between sections
4. Verify Form 470 search results

## 📊 Performance

### Asana Form Agent Performance:
- **Processing Speed:** ~30-60 seconds per task
- **API Rate Limits:** Respects Asana and USAC API limits
- **Memory Usage:** Minimal, temporary PDF storage only
- **Concurrent Processing:** Single-threaded for reliability

### Finance Agent Performance:
- **Response Time:** 5-15 seconds per query
- **Data Freshness:** Real-time from Yahoo Finance
- **Analysis Depth:** Comprehensive financial metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify environment variables are set correctly
3. Test with the included test scripts
4. Review Asana API documentation for section management

---

**Built with Agno Framework** - Fast, clean, and production-ready AI agent development.
