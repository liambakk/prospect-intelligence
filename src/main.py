"""
Prospect Intelligence Tool - Main FastAPI Application
For ModelML Sales Demo
"""

from fastapi import FastAPI, HTTPException, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import os
from dotenv import load_dotenv
from services.clearbit_service import ClearbitService
from services.hunter_service import HunterService
from services.web_scraper import WebScraperService
from services.scoring_engine import AIReadinessScoringEngine
from services.job_posting_service import JobPostingService
from services.report_generator import PDFReportGenerator
from services.news_service import NewsService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="Prospect Intelligence Tool",
    description="Automated AI readiness assessment for ModelML prospects",
    version="1.0.0"
)

# Add rate limit error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize services
# Try Hunter.io first (free tier available), fallback to Clearbit
hunter_service = HunterService()
clearbit_service = ClearbitService()
web_scraper = WebScraperService()
scoring_engine = AIReadinessScoringEngine()
job_posting_service = JobPostingService()
pdf_generator = PDFReportGenerator()
news_service = NewsService()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class CompanyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Company name")
    domain: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$', description="Company domain")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Company name cannot be empty')
        return v.strip()

class HealthResponse(BaseModel):
    status: str
    version: str
    message: str

class ProspectAnalysisResponse(BaseModel):
    company_name: str
    domain: Optional[str] = None
    ai_readiness_score: int
    confidence: float
    message: str
    company_data: Optional[Dict[str, Any]] = None

# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Web interface not found. Please check static/index.html</h1>", status_code=404)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        message="All systems operational"
    )

@app.post("/analyze", response_model=ProspectAnalysisResponse)
@limiter.limit("10/minute")
async def analyze_prospect(request: Request, company: CompanyRequest):
    """
    Analyze a company's AI readiness
    
    Args:
        company: CompanyRequest with company name and optional domain
    
    Returns:
        ProspectAnalysisResponse with AI readiness score and details
    """
    try:
        company_data = None
        score = 50  # Base score
        confidence = 0.3
        company_name = company.name
        
        if company.domain:
            # Try Hunter.io first (free tier available)
            hunter_data = await hunter_service.search_domain(company.domain)
            
            if hunter_data:
                company_name = hunter_data.organization or company.name
                
                # Build company data from Hunter.io
                company_data = {
                    "name": company_name,
                    "industry": hunter_data.company_industry,
                    "size": hunter_data.company_size,
                    "location": f"{hunter_data.city}, {hunter_data.state} {hunter_data.country}".strip(),
                    "technologies": hunter_data.technologies,
                    "contacts_found": hunter_data.email_count,
                    "key_contacts": hunter_data.contacts[:3] if hunter_data.contacts else [],
                    "social": {
                        "linkedin": hunter_data.linkedin,
                        "twitter": hunter_data.twitter,
                        "facebook": hunter_data.facebook
                    }
                }
                
                # Calculate AI readiness score based on Hunter.io data
                score = 40  # Base score
                
                # Company size scoring
                if hunter_data.company_size:
                    if "10000+" in hunter_data.company_size:
                        score += 20
                    elif "1000" in hunter_data.company_size:
                        score += 15
                    elif "100" in hunter_data.company_size or "500" in hunter_data.company_size:
                        score += 12
                    else:
                        score += 8
                
                # Technology stack scoring
                if hunter_data.technologies:
                    ai_keywords = ["tensorflow", "pytorch", "python", "aws", "ml", "ai", "data", "kubernetes", "docker"]
                    tech_lower = [t.lower() for t in hunter_data.technologies]
                    ai_tech_count = sum(1 for keyword in ai_keywords if any(keyword in tech for tech in tech_lower))
                    score += min(ai_tech_count * 4, 25)
                
                # Industry scoring
                if hunter_data.company_industry:
                    industry_lower = hunter_data.company_industry.lower()
                    if any(x in industry_lower for x in ["artificial", "ai", "machine learning", "technology"]):
                        score += 15
                    elif any(x in industry_lower for x in ["software", "internet", "financial", "banking"]):
                        score += 10
                    else:
                        score += 5
                
                # Executive contacts bonus
                if hunter_data.contacts:
                    executive_count = sum(1 for c in hunter_data.contacts if c.get("seniority") == "executive")
                    score += min(executive_count * 3, 10)
                
                score = min(score, 100)
                confidence = 0.8
                
                return ProspectAnalysisResponse(
                    company_name=company_name,
                    domain=company.domain,
                    ai_readiness_score=score,
                    confidence=confidence,
                    message=f"Analysis complete for {company_name} using Hunter.io data",
                    company_data=company_data
                )
            
            # Fallback to Clearbit if Hunter.io doesn't have data
            else:
                clearbit_data = await clearbit_service.get_company_data(company.domain)
                if clearbit_data:
                    company_name = clearbit_data.name
                    company_data = {
                        "name": clearbit_data.name,
                        "industry": clearbit_data.industry,
                        "employees": clearbit_data.employee_count,
                        "headquarters": clearbit_data.headquarters,
                        "description": clearbit_data.description,
                        "tech_stack": clearbit_data.tech_stack,
                        "founded_year": clearbit_data.founded_year
                    }
                    
                    # Scoring based on Clearbit data
                    score = 50
                    if clearbit_data.employee_count:
                        if clearbit_data.employee_count > 1000:
                            score += 20
                        elif clearbit_data.employee_count > 100:
                            score += 15
                        else:
                            score += 10
                    
                    if clearbit_data.tech_stack:
                        ai_keywords = ["tensorflow", "pytorch", "scikit", "ml", "ai", "data"]
                        tech_lower = [t.lower() for t in clearbit_data.tech_stack]
                        ai_tech_count = sum(1 for keyword in ai_keywords if any(keyword in tech for tech in tech_lower))
                        score += min(ai_tech_count * 5, 20)
                    
                    score = min(score, 100)
                    confidence = 0.75
                    
                    return ProspectAnalysisResponse(
                        company_name=company_name,
                        domain=company.domain,
                        ai_readiness_score=score,
                        confidence=confidence,
                        message=f"Analysis complete for {company_name} using Clearbit data",
                        company_data=company_data
                    )
        
        # No domain provided or no data found
        return ProspectAnalysisResponse(
            company_name=company_name,
            domain=company.domain,
            ai_readiness_score=50,
            confidence=0.3,
            message=f"Limited data available for {company_name}. Provide domain for better analysis.",
            company_data=None
        )
        
    except Exception as e:
        logging.error(f"Error analyzing prospect: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/docs")
async def api_documentation():
    """API documentation endpoint"""
    return {
        "endpoints": {
            "/": "Health check",
            "/health": "Detailed health check",
            "/analyze": "POST - Analyze company AI readiness",
            "/api/docs": "This documentation",
            "/api/account": "Hunter.io account info and remaining searches"
        },
        "version": "1.0.0"
    }

@app.get("/api/account")
async def account_info():
    """Get Hunter.io account information and remaining searches"""
    account = hunter_service.get_account_info()
    return {
        "hunter_io": account if account else {"status": "No API key configured, using mock data"},
        "message": "Hunter.io provides 25 free searches/month. Sign up at https://hunter.io/users/sign-up"
    }

@app.post("/analyze/comprehensive")
@limiter.limit("10/minute")
async def analyze_comprehensive(request: Request, company: CompanyRequest):
    """
    Comprehensive AI readiness analysis using all data sources
    """
    try:
        # 1. Collect data from Hunter.io
        hunter_data = None
        if company.domain:
            hunter_result = await hunter_service.search_domain(company.domain)
            if hunter_result:
                hunter_data = {
                    "organization": hunter_result.organization,
                    "industry": hunter_result.company_industry,
                    "size": hunter_result.company_size,
                    "location": f"{hunter_result.city}, {hunter_result.state} {hunter_result.country}".strip(),
                    "key_contacts": hunter_result.contacts[:5] if hunter_result.contacts else []
                }
        
        # 2. Scrape website for tech signals
        web_data = None
        if company.domain:
            web_data = await web_scraper.scrape_company_website(company.domain)
        
        # 3. Collect job posting data
        job_data = None
        if company.name:
            job_data = await job_posting_service.search_company_jobs(company.name)
        
        # 4. Collect news and press releases
        news_data = None
        if company.name:
            news_data = await news_service.get_company_news(company.name, days_back=30)
        
        # 5. Try Clearbit as fallback for additional data
        clearbit_data = None
        if company.domain and not hunter_data:
            clearbit_result = await clearbit_service.get_company_data(company.domain)
            if clearbit_result:
                clearbit_data = {
                    "name": clearbit_result.name,
                    "industry": clearbit_result.industry,
                    "employees": clearbit_result.employee_count,
                    "tech_stack": clearbit_result.tech_stack
                }
        
        # 6. Calculate comprehensive score
        scoring_result = scoring_engine.calculate_ai_readiness_score(
            hunter_data=hunter_data,
            web_scraping_data=web_data,
            clearbit_data=clearbit_data,
            job_posting_data=job_data,
            news_data=news_data
        )
        
        # 5. Compile comprehensive response
        company_name = company.name
        if hunter_data and hunter_data.get("organization"):
            company_name = hunter_data["organization"]
        elif clearbit_data and clearbit_data.get("name"):
            company_name = clearbit_data["name"]
        
        return {
            "company_name": company_name,
            "domain": company.domain,
            "ai_readiness_score": scoring_result["overall_score"],
            "readiness_category": scoring_result["readiness_category"],
            "confidence": scoring_result["confidence"],
            "component_scores": scoring_result["component_scores"],
            "key_strengths": scoring_result["key_strengths"],
            "improvement_areas": scoring_result["improvement_areas"],
            "recommendations": scoring_result["recommendations"],
            "data_sources": {
                "hunter_io": hunter_data is not None,
                "web_scraping": web_data is not None and web_data.get("ai_mentions_count", 0) > 0,
                "job_postings": job_data is not None and job_data.get("total_jobs_found", 0) > 0,
                "news_articles": news_data is not None and news_data.get("articles_processed", 0) > 0,
                "clearbit": clearbit_data is not None
            },
            "company_data": {
                "basic_info": hunter_data or clearbit_data or {},
                "tech_signals": {
                    "ai_mentions": web_data.get("ai_mentions_count", 0) if web_data else 0,
                    "tech_stack": web_data.get("tech_stack_detected", []) if web_data else [],
                    "ai_roles_hiring": web_data.get("careers_signals", {}).get("ai_roles", []) if web_data else []
                },
                "job_postings": {
                    "total_jobs": job_data.get("total_jobs_found", 0) if job_data else 0,
                    "ai_ml_jobs": job_data.get("ai_ml_jobs_count", 0) if job_data else 0,
                    "tech_jobs": job_data.get("tech_jobs_count", 0) if job_data else 0,
                    "ai_hiring_intensity": job_data.get("ai_hiring_intensity", "none") if job_data else "none",
                    "top_ai_technologies": job_data.get("top_ai_technologies", [])[:5] if job_data else [],
                    "recent_titles": job_data.get("recent_job_titles", [])[:5] if job_data else []
                },
                "news_insights": {
                    "total_articles": news_data.get("total_articles_found", 0) if news_data else 0,
                    "articles_analyzed": news_data.get("articles_processed", 0) if news_data else 0,
                    "tech_focus_score": news_data.get("tech_focus_score", 0) if news_data else 0,
                    "recent_trends": news_data.get("recent_trends", []) if news_data else [],
                    "top_articles": news_data.get("articles", [])[:3] if news_data else []
                }
            }
        }
        
    except Exception as e:
        logging.error(f"Error in comprehensive analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/generate-report")
@limiter.limit("5/minute")
async def generate_pdf_report(request: Request, company: CompanyRequest):
    """
    Generate a PDF report for a company's AI readiness assessment
    """
    try:
        # First, run comprehensive analysis
        analysis_result = await analyze_comprehensive(company)
        
        # Generate PDF report
        report_path = pdf_generator.generate_report(
            company_name=company.name,
            ai_readiness_data=analysis_result
        )
        
        # Return file for download
        from fastapi.responses import FileResponse
        import os
        
        if os.path.exists(report_path):
            return FileResponse(
                path=report_path,
                media_type='application/pdf',
                filename=os.path.basename(report_path)
            )
        else:
            raise HTTPException(status_code=500, detail="Report generation failed")
            
    except Exception as e:
        logging.error(f"Error generating PDF report: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.get("/reports/{filename}")
async def download_report(filename: str):
    """
    Download a previously generated report
    """
    from fastapi.responses import FileResponse
    import os
    
    report_path = f"reports/{filename}"
    
    if os.path.exists(report_path):
        return FileResponse(
            path=report_path,
            media_type='application/pdf',
            filename=filename
        )
    else:
        raise HTTPException(status_code=404, detail="Report not found")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time progress updates
    """
    await websocket.accept()
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to progress updates",
            "progress": 0
        })
        
        # In a real implementation, you would send actual progress updates
        # during the analysis process. For now, we'll just keep the connection open
        while True:
            # Wait for any message from client (heartbeat)
            data = await websocket.receive_text()
            
            # Echo back a heartbeat
            await websocket.send_json({
                "type": "heartbeat",
                "message": "Connection active"
            })
            
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    # Run with uvicorn when executed directly
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )