"""
Prospect Intelligence Tool - Main FastAPI Application
For ModelML Sales Demo
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Prospect Intelligence Tool",
    description="Automated AI readiness assessment for ModelML prospects",
    version="1.0.0"
)

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
    name: str
    domain: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    message: str

class ProspectAnalysisResponse(BaseModel):
    company_name: str
    ai_readiness_score: int
    confidence: float
    message: str

# Routes
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        message="Prospect Intelligence Tool is running"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        message="All systems operational"
    )

@app.post("/analyze", response_model=ProspectAnalysisResponse)
async def analyze_prospect(company: CompanyRequest):
    """
    Analyze a company's AI readiness
    
    Args:
        company: CompanyRequest with company name and optional domain
    
    Returns:
        ProspectAnalysisResponse with AI readiness score and details
    """
    # Placeholder implementation - will be replaced with actual logic
    return ProspectAnalysisResponse(
        company_name=company.name,
        ai_readiness_score=75,  # Placeholder score
        confidence=0.85,
        message=f"Analysis for {company.name} will be implemented in upcoming tasks"
    )

@app.get("/api/docs")
async def api_documentation():
    """API documentation endpoint"""
    return {
        "endpoints": {
            "/": "Health check",
            "/health": "Detailed health check",
            "/analyze": "POST - Analyze company AI readiness",
            "/api/docs": "This documentation"
        },
        "version": "1.0.0"
    }

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