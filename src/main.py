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
from services.financial_scoring_engine import FinancialAIReadinessScoringEngine
from services.job_posting_service import JobPostingService
from services.report_generator import PDFReportGenerator
from services.enhanced_report_generator import EnhancedPDFReportGenerator
from services.news_service import NewsService
from services.company_database import CompanyDatabase
from services.decision_maker_service import DecisionMakerService
from services.brightdata_service import BrightDataService
from services.brightdata_linkedin_service import BrightDataLinkedInService
from services.brightdata_correct_service import BrightDataCorrectService
from services.ai_recommendation_service import AIRecommendationService
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
financial_scoring_engine = FinancialAIReadinessScoringEngine()
job_posting_service = JobPostingService()
pdf_generator = PDFReportGenerator()
enhanced_pdf_generator = EnhancedPDFReportGenerator()
news_service = NewsService()
company_database = CompanyDatabase()
decision_maker_service = DecisionMakerService()
brightdata_service = BrightDataService()
brightdata_linkedin_service = BrightDataLinkedInService()
brightdata_correct_service = BrightDataCorrectService()
ai_recommendation_service = AIRecommendationService()

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
                    "key_contacts": hunter_result.contacts[:5] if hunter_result.contacts else [],
                    "technologies": hunter_result.technologies if hunter_result.technologies else []
                }
        
        # 2. Scrape website for tech signals
        web_data = None
        if company.domain:
            web_data = await web_scraper.scrape_company_website(company.domain)
        
        # 3. Collect job posting data
        job_data = None
        if company.name:
            job_data = await job_posting_service.search_company_jobs(company.name)
        
        # 4. Try Clearbit as fallback for additional data
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
        
        # 5. Detect if it's a financial company
        is_financial = financial_scoring_engine.detect_financial_company(
            hunter_data=hunter_data,
            clearbit_data=clearbit_data,
            company_name=company.name
        )
        
        # 6. Collect news and press releases (with financial focus if applicable)
        news_data = None
        if company.name:
            news_data = await news_service.get_company_news(
                company.name, 
                days_back=30,
                is_financial=is_financial
            )
        
        # 7. Get enhanced LinkedIn data from BrightData
        linkedin_company = None
        brightdata_decision_makers = []
        if company.name:
            # Use the corrected BrightData service to search for decision makers
            brightdata_decision_makers = await brightdata_correct_service.search_linkedin_profiles(company.name)
            
            # Extract company info from the first profile if available
            if brightdata_decision_makers and len(brightdata_decision_makers) > 0:
                first_profile = brightdata_decision_makers[0]
                linkedin_company = {
                    "name": company.name,
                    "employee_count": sum(p.get("connections", 0) for p in brightdata_decision_makers),
                    "follower_count": sum(p.get("followers", 0) for p in brightdata_decision_makers),
                    "recent_updates": [p.get("recent_activity", "") for p in brightdata_decision_makers[:3] if p.get("recent_activity")]
                }
        
        # 8. Identify key decision makers (combine Hunter.io and BrightData)
        decision_makers = decision_maker_service.identify_decision_makers(
            hunter_data=hunter_data,
            company_name=company.name,
            is_financial=is_financial
        )
        
        # Enhance with BrightData LinkedIn profiles
        if brightdata_decision_makers:
            for bd_dm in brightdata_decision_makers[:3]:  # Add top 3 from BrightData
                skills = bd_dm.get("skills", [])
                experience_years = bd_dm.get("experience_years", 0)
                about = bd_dm.get("about", "")[:100] if bd_dm.get("about") else ""
                
                decision_makers.insert(0, {
                    "name": bd_dm.get("name", "Unknown"),
                    "title": bd_dm.get("title", "Unknown"),
                    "email": "",  # LinkedIn doesn't provide emails
                    "linkedin": bd_dm.get("linkedin_url", ""),
                    "priority": 1,  # High priority for LinkedIn verified profiles
                    "role": "LinkedIn Verified Profile",
                    "approach": f"Personalized LinkedIn outreach - {bd_dm.get('title', 'Executive')}",
                    "confidence": 95,
                    "skills": skills,
                    "experience_years": experience_years,
                    "followers": bd_dm.get("followers", 0),
                    "connections": bd_dm.get("connections", 0),
                    "about_snippet": about,
                    "recent_activity": bd_dm.get("recent_activity", ""),
                    "education": bd_dm.get("education", ""),
                    "talking_points": [
                        f"Connect on expertise in {', '.join(skills[:2])}" if skills else "Discuss industry trends",
                        f"Reference their {experience_years}+ years of experience" if experience_years > 0 else "Acknowledge their leadership role",
                        f"Recent activity: {bd_dm.get('recent_activity', '')[:50]}" if bd_dm.get("recent_activity") else "ModelML's value for your role",
                        "How ModelML accelerates AI initiatives at scale"
                    ]
                })
        
        # 8. Calculate comprehensive score using appropriate engine
        if is_financial:
            scoring_result = financial_scoring_engine.calculate_financial_ai_readiness(
                hunter_data=hunter_data,
                web_scraping_data=web_data,
                clearbit_data=clearbit_data,
                job_posting_data=job_data,
                news_data=news_data
            )
        else:
            scoring_result = scoring_engine.calculate_ai_readiness_score(
                hunter_data=hunter_data,
                web_scraping_data=web_data,
                clearbit_data=clearbit_data,
                job_posting_data=job_data,
                news_data=news_data
            )
        
        # 9. Generate AI-powered recommendations
        # Prepare company data for AI recommendation service
        company_analysis_data = {
            "job_postings": job_data,
            "news_insights": news_data,
            "tech_signals": web_data,
            "linkedin_profile": linkedin_company,
            "basic_info": hunter_data or clearbit_data or {}
        }
        
        # Generate AI-powered sales recommendations
        ai_recommendations = await ai_recommendation_service.generate_sales_recommendations(
            company_name=company.name,
            ai_readiness_score=scoring_result["overall_score"],
            component_scores=scoring_result["component_scores"],
            company_data=company_analysis_data,
            decision_makers=decision_makers,
            is_financial=is_financial
        )
        
        # Generate personalized outreach for top decision makers
        personalized_outreach = []
        for dm in decision_makers[:3]:  # Top 3 decision makers
            outreach = await ai_recommendation_service.generate_personalized_outreach(
                decision_maker=dm,
                company_name=company.name,
                ai_readiness_score=scoring_result["overall_score"],
                key_insights=scoring_result.get("key_strengths", []) + scoring_result.get("improvement_areas", [])
            )
            dm["personalized_outreach"] = outreach
            personalized_outreach.append(outreach)
        
        # Combine AI recommendations with existing outreach strategy
        outreach_strategy = decision_maker_service.generate_outreach_strategy(
            decision_makers=decision_makers,
            ai_readiness_score=scoring_result["overall_score"],
            company_name=company.name
        )
        
        # Merge AI recommendations into outreach strategy
        if ai_recommendations:
            outreach_strategy["ai_recommendations"] = ai_recommendations
            outreach_strategy["priority"] = ai_recommendations.get("priority_level", "medium")
            outreach_strategy["estimated_deal_size"] = ai_recommendations.get("estimated_deal_size", "Unknown")
            outreach_strategy["timeline"] = ai_recommendations.get("timeline", "3-6 months")
        
        # 10. Compile comprehensive response
        company_name = company.name
        if hunter_data and hunter_data.get("organization"):
            company_name = hunter_data["organization"]
        elif clearbit_data and clearbit_data.get("name"):
            company_name = clearbit_data["name"]
        
        # Format decision makers for response
        formatted_decision_makers = []
        for dm in decision_makers[:5]:  # Top 5 decision makers
            formatted_dm = {
                "name": dm.get("name", "Unknown"),
                "title": dm.get("title", "Unknown"),
                "role": dm.get("role", "Decision Maker"),
                "approach": dm.get("approach", "Standard outreach"),
                "priority": dm.get("priority", 3),
                "talking_points": dm.get("talking_points", [])
            }
            if dm.get("email"):
                formatted_dm["email"] = dm["email"]
            if dm.get("linkedin"):
                formatted_dm["linkedin"] = dm["linkedin"]
            formatted_decision_makers.append(formatted_dm)
        
        response_data = {
            "company_name": company_name,
            "domain": company.domain,
            "ai_readiness_score": scoring_result["overall_score"],
            "readiness_category": scoring_result["readiness_category"],
            "confidence": scoring_result["confidence"],
            "component_scores": scoring_result["component_scores"],
            "key_strengths": scoring_result["key_strengths"],
            "improvement_areas": scoring_result["improvement_areas"],
            "recommendations": {
                "decision_makers": formatted_decision_makers,
                "sales_approach": outreach_strategy,
                "ai_powered_strategy": ai_recommendations if ai_recommendations else None,
                "priority_level": ai_recommendations.get("priority_level", "medium") if ai_recommendations else "medium",
                "estimated_deal_size": ai_recommendations.get("estimated_deal_size", "$500K-$1M") if ai_recommendations else "$500K-$1M",
                "key_talking_points": ai_recommendations.get("key_talking_points", []) if ai_recommendations else outreach_strategy.get("messaging", "").split("\n"),
                "recommended_use_cases": ai_recommendations.get("recommended_use_cases", []) if ai_recommendations else [],
                "objection_handling": ai_recommendations.get("objection_handling", []) if ai_recommendations else [],
                "next_steps": ai_recommendations.get("next_steps", []) if ai_recommendations else [
                    f"Target {len(formatted_decision_makers)} identified decision makers",
                    f"Use {outreach_strategy.get('approach', 'standard')} approach",
                    f"Timeline: {outreach_strategy.get('timeline', '2-4 weeks')}",
                    "Prepare customized demo focusing on identified use cases"
                ],
                "competitive_positioning": ai_recommendations.get("competitive_positioning", "") if ai_recommendations else "",
                "success_metrics": ai_recommendations.get("success_metrics", []) if ai_recommendations else []
            },
            "is_financial_company": is_financial,
            "data_sources": {
                "hunter_io": hunter_data is not None,
                "web_scraping": web_data is not None and web_data.get("ai_mentions_count", 0) > 0,
                "job_postings": job_data is not None and job_data.get("total_jobs_found", 0) > 0,
                "news_articles": news_data is not None and news_data.get("articles_processed", 0) > 0,
                "clearbit": clearbit_data is not None,
                "linkedin": linkedin_company is not None,
                "brightdata": len(brightdata_decision_makers) > 0
            },
            "company_data": {
                "basic_info": hunter_data or clearbit_data or {},
                "linkedin_profile": {
                    "company_size": linkedin_company.get("size") if linkedin_company else None,
                    "employee_count": linkedin_company.get("employee_count") if linkedin_company else None,
                    "follower_count": linkedin_company.get("follower_count") if linkedin_company else None,
                    "specialties": linkedin_company.get("specialties", []) if linkedin_company else [],
                    "recent_updates": linkedin_company.get("recent_updates", [])[:3] if linkedin_company else [],
                    "founded": linkedin_company.get("founded") if linkedin_company else None
                } if linkedin_company else {},
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
        
        # Add financial-specific insights if applicable
        if is_financial and "financial_insights" in scoring_result:
            response_data["financial_insights"] = scoring_result["financial_insights"]
            response_data["scoring_methodology"] = scoring_result.get("scoring_methodology", "Financial Services Optimized")
        
        return response_data
        
    except Exception as e:
        logging.error(f"Error in comprehensive analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/generate-report")
@limiter.limit("5/minute")
async def generate_pdf_report(request: Request, analysis_data: Dict[str, Any]):
    """
    Generate a PDF report for a company's AI readiness assessment
    """
    try:
        # Extract company info from the analysis data
        company_name = analysis_data.get("company_name", "Unknown Company")
        domain = analysis_data.get("domain")
        
        # Generate PDF report with enhanced design
        report_path = enhanced_pdf_generator.generate_report(
            company_name=company_name,
            ai_readiness_data=analysis_data
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

@app.get("/api/company-suggestions")
async def get_company_suggestions(q: str = None):
    """
    Get company name suggestions for autocomplete
    
    Args:
        q: Query string for company search
    
    Returns:
        List of matching companies with details
    """
    if not q or len(q) < 2:
        return {"suggestions": []}
    
    try:
        # Search for matching companies
        logging.info(f"Searching for companies with query: {q}")
        suggestions = company_database.search_companies(q, limit=8)
        logging.info(f"Found {len(suggestions)} suggestions for query: {q}")
        
        # Format response for frontend
        formatted_suggestions = []
        for company in suggestions:
            formatted_suggestions.append({
                "name": company["name"],
                "ticker": company.get("ticker", ""),
                "type": company.get("type", "Company"),
                "sector": company.get("sector", ""),
            })
        
        return {"suggestions": formatted_suggestions}
    
    except Exception as e:
        logging.error(f"Error fetching company suggestions: {e}")
        return {"suggestions": []}

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