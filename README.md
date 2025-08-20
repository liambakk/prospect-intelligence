# 🎯 Prospect Intelligence Tool

An AI-powered sales intelligence platform that analyzes companies' AI readiness and generates personalized sales strategies for ModelML's sales team. Built as a demonstration of technical capability and sales process understanding.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Features

- **AI Readiness Scoring**: Analyzes companies on a 0-100 scale based on multiple data points
- **Real-Time Data Collection**: Aggregates data from multiple sources (Hunter.io, NewsAPI, JSearch, web scraping)
- **AI-Powered Recommendations**: Uses OpenAI GPT-4 to generate personalized sales strategies
- **Financial Services Optimization**: Special scoring algorithm for banks and financial institutions
- **Decision Maker Identification**: Finds and profiles key executives with contact information
- **Interactive Web Interface**: Modern, responsive UI with real-time progress tracking
- **PDF Report Generation**: Professional reports for sales teams
- **Company Autocomplete**: Quick search with 120+ pre-loaded companies

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git
- 4GB RAM minimum
- Active internet connection

## 🛠️ Quick Setup (5 Minutes)

### 1. Clone the Repository

```bash
git clone https://github.com/liambakk/prospect-intelligence.git
cd prospect-intelligence
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the root directory:

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your API keys
nano .env  # or use any text editor
```

Add your API keys to the `.env` file:

```bash
# REQUIRED - At least one of these for company data
HUNTER_API_KEY=your_hunter_api_key_here        # Free tier: 25 searches/month
CLEARBIT_API_KEY=your_clearbit_key_here        # Optional fallback

# REQUIRED - For job postings
RAPIDAPI_KEY=your_rapidapi_key_here            # For JSearch API

# REQUIRED - For news analysis
NEWS_API_KEY=your_newsapi_key_here             # Free tier: 100 requests/day

# OPTIONAL BUT RECOMMENDED - For AI-powered recommendations
OPENAI_API_KEY=your_openai_api_key_here        # For GPT-4 recommendations

# OPTIONAL - BrightData for LinkedIn (disabled by default - too slow)
BRIGHT_DATA_API=your_brightdata_key_here       # Not recommended
```

#### 🔑 Getting API Keys (Free Tiers Available)

1. **Hunter.io** (Free: 25 searches/month) - **5 minutes**
   - Sign up at: https://hunter.io/users/sign_up
   - Get API key from: https://hunter.io/api_keys

2. **NewsAPI** (Free: 100 requests/day) - **2 minutes**
   - Sign up at: https://newsapi.org/register
   - Key is instantly available after registration

3. **RapidAPI** (Free tier available) - **5 minutes**
   - Sign up at: https://rapidapi.com/auth/sign-up
   - Subscribe to JSearch API: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
   - Click "Subscribe to Test" (free tier)

4. **OpenAI** (Optional but recommended) - **5 minutes**
   - Sign up at: https://platform.openai.com/signup
   - Create API key: https://platform.openai.com/api-keys
   - Add $5 credit for ~150 analyses

### 5. Run the Application

```bash
# Start the server (default port 8000)
python src/main.py

# The server will start with output like:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Alternative ports** if 8000 is in use:

```bash
# Use port 8080
uvicorn src.main:app --host 0.0.0.0 --port 8080

# Use port 3000
uvicorn src.main:app --host 0.0.0.0 --port 3000
```

### 6. Access the Application

Open your browser and navigate to:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## 🎮 Using the Application

### Web Interface (Recommended)

1. **Open** http://localhost:8000 in your browser
2. **Type** a company name (autocomplete helps after 2 characters)
3. **Select** from suggestions or press Enter
4. **Watch** the animated progress (10-20 seconds)
5. **Review** comprehensive results:
   - AI Readiness Score with visual gauge
   - Component breakdown (radar chart)
   - Key decision makers with contact info
   - AI-powered sales recommendations
   - Personalized talking points
6. **Download** PDF report for offline use

### Quick Test Companies

Try these for best results:

```
Technology:
- Microsoft
- Apple
- Google
- Amazon
- Tesla

Financial Services:
- JPMorgan Chase
- Goldman Sachs
- Bank of America
- BlackRock
- Intesa Sanpaolo

Other:
- Walmart
- Coca-Cola
- Johnson & Johnson
```

### API Usage

```bash
# Basic analysis
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"name": "Microsoft", "domain": "microsoft.com"}'

# Comprehensive analysis (recommended)
curl -X POST http://localhost:8000/analyze/comprehensive \
  -H "Content-Type: application/json" \
  -d '{"name": "JPMorgan Chase", "domain": "jpmorganchase.com"}'

# Company autocomplete
curl "http://localhost:8000/api/company-suggestions?q=app"
```

## 🏗️ Project Structure

```
prospect-intelligence/
├── src/
│   ├── main.py                          # FastAPI application & routes
│   └── services/
│       ├── ai_recommendation_service.py # OpenAI GPT-4 integration
│       ├── company_database.py          # 120+ companies for autocomplete
│       ├── decision_maker_service.py    # Executive identification
│       ├── financial_scoring_engine.py  # Financial sector specialization
│       ├── hunter_service.py            # Email & contact finder
│       ├── job_posting_service.py       # Job market analysis (JSearch)
│       ├── news_service.py              # News sentiment (NewsAPI)
│       ├── scoring_engine.py            # AI readiness algorithm
│       └── web_scraper.py               # Website tech analysis
├── static/
│   ├── index.html                       # Modern web interface
│   ├── css/style.css                    # Professional styling
│   └── js/app.js                        # Interactive features
├── reports/                             # Generated PDF reports
├── requirements.txt                     # Python dependencies
├── .env                                 # Your API keys (create this)
├── .env.example                         # Template for API keys
└── README.md                            # This file
```

## ⚙️ Configuration Options

### Environment Variables (.env)

```bash
# Server Configuration
PORT=8000                               # Change if 8000 is in use
ENVIRONMENT=development                 # or 'production'

# Optional Performance Tuning
DATABASE_URL=sqlite:///./prospect_intelligence.db
REDIS_URL=redis://localhost:6379/0      # For caching (optional)

# API Keys (see setup section above)
HUNTER_API_KEY=xxx
NEWS_API_KEY=xxx
RAPIDAPI_KEY=xxx
OPENAI_API_KEY=xxx                      # Highly recommended
```

## 🐛 Troubleshooting

### Common Issues & Solutions

**1. Port 8000 already in use**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9           # macOS/Linux
netstat -ano | findstr :8000            # Windows (then kill PID)

# Or use different port
python src/main.py --port 8080
```

**2. ModuleNotFoundError**
```bash
# Ensure virtual environment is activated
which python                             # Should show venv path
source venv/bin/activate                # Reactivate if needed
pip install -r requirements.txt         # Reinstall dependencies
```

**3. API Key Errors**
- Check `.env` file exists in root directory
- No quotes needed around keys in `.env`
- Restart server after adding keys
- Verify keys are active on provider dashboards

**4. Analysis Hangs or Times Out**
- Normal analysis: 10-20 seconds
- If hanging: BrightData may be enabled (disabled by default)
- Frontend timeout: 120 seconds (adjustable in `static/js/app.js`)

**5. No Autocomplete Suggestions**
```bash
# Server should show:
INFO:services.company_database:CompanyDatabase initialized with 121 companies

# If not, restart server:
CTRL+C
python src/main.py
```

## 📊 Performance & Limits

### API Rate Limits (Free Tiers)
- **Hunter.io**: 25 searches/month
- **NewsAPI**: 100 requests/day  
- **JSearch**: 100 searches/month (free tier)
- **OpenAI**: Pay-per-use (~$0.03 per analysis)

### Response Times
- Company autocomplete: <100ms
- Basic analysis: 5-10 seconds
- Comprehensive analysis: 10-20 seconds
- PDF generation: 2-3 seconds

### Caching
- API responses cached for 15 minutes
- Reduces API calls for repeated analyses
- Clear cache by restarting server

## 🚀 Production Deployment

For production use, consider:

```bash
# Use production server
pip install gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# With Docker
docker build -t prospect-intelligence .
docker run -p 8000:8000 --env-file .env prospect-intelligence

# Environment variables for production
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379/0
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/NewFeature`)
3. Commit changes (`git commit -m 'Add NewFeature'`)
4. Push to branch (`git push origin feature/NewFeature`)
5. Open Pull Request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built for ModelML sales team demonstration
- Showcases AI-powered sales intelligence capabilities
- Demonstrates understanding of B2B sales processes
- Integrates multiple data sources for comprehensive analysis

## 📧 Support

**Issues**: https://github.com/liambakk/prospect-intelligence/issues
**Author**: Liam Bakker
**Repository**: https://github.com/liambakk/prospect-intelligence

---

**Quick Start Summary:**
1. Clone repo: `git clone https://github.com/liambakk/prospect-intelligence.git`
2. Setup venv: `python3 -m venv venv && source venv/bin/activate`
3. Install: `pip install -r requirements.txt`
4. Add API keys to `.env` file
5. Run: `python src/main.py`
6. Open: http://localhost:8000

**Total Setup Time: ~10 minutes** with API key registration