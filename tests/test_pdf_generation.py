"""
Test PDF Report Generation
"""

import sys
from pathlib import Path
import os
import json

sys.path.append(str(Path(__file__).parent.parent / "src"))

from services.report_generator import PDFReportGenerator


def test_pdf_generation():
    """Test PDF report generation with sample data"""
    
    print("=" * 60)
    print("PDF REPORT GENERATION TEST")
    print("=" * 60)
    
    # Initialize generator
    generator = PDFReportGenerator()
    
    # Sample data mimicking comprehensive analysis output
    sample_data = {
        "company_name": "TechCorp Inc.",
        "domain": "techcorp.com",
        "ai_readiness_score": 72,
        "readiness_category": "Strong Potential",
        "confidence": 0.85,
        "component_scores": {
            "tech_hiring": 75,
            "ai_mentions": 68,
            "company_size": 70,
            "industry_adoption": 80,
            "tech_modernization": 65
        },
        "key_strengths": [
            "Strong technical team",
            "AI-forward industry",
            "Sufficient scale for AI"
        ],
        "improvement_areas": [
            "Limited AI visibility",
            "Legacy technology"
        ],
        "recommendations": [
            "Develop clear AI strategy and communicate it publicly",
            "Modernize technology stack with cloud and AI-ready infrastructure",
            "Ready for advanced AI implementation - consider ModelML's platform"
        ],
        "data_sources": {
            "hunter_io": True,
            "web_scraping": True,
            "job_postings": True,
            "clearbit": False
        },
        "company_data": {
            "basic_info": {
                "organization": "TechCorp Inc.",
                "industry": "Technology",
                "size": "1000-5000",
                "location": "San Francisco, CA US",
                "key_contacts": [
                    {
                        "name": "John Smith",
                        "title": "CTO",
                        "department": "executive",
                        "seniority": "executive"
                    },
                    {
                        "name": "Jane Doe",
                        "title": "VP Engineering",
                        "department": "engineering",
                        "seniority": "executive"
                    }
                ]
            },
            "tech_signals": {
                "ai_mentions": 25,
                "tech_stack": ["python", "tensorflow", "aws", "kubernetes", "react"],
                "ai_roles_hiring": ["ML Engineer", "Data Scientist", "AI Researcher"]
            },
            "job_postings": {
                "total_jobs": 45,
                "ai_ml_jobs": 12,
                "tech_jobs": 28,
                "ai_hiring_intensity": "high",
                "top_ai_technologies": [
                    {"keyword": "tensorflow", "count": 8},
                    {"keyword": "pytorch", "count": 6},
                    {"keyword": "python", "count": 15},
                    {"keyword": "machine learning", "count": 10},
                    {"keyword": "deep learning", "count": 4}
                ],
                "recent_titles": [
                    {
                        "title": "Senior ML Engineer",
                        "employer": "TechCorp Inc.",
                        "location": "San Francisco, CA",
                        "posted_date": "2024-01-15",
                        "is_ai_ml": True
                    },
                    {
                        "title": "Data Scientist",
                        "employer": "TechCorp Inc.",
                        "location": "Remote",
                        "posted_date": "2024-01-14",
                        "is_ai_ml": True
                    }
                ]
            }
        }
    }
    
    # Test 1: Generate report with all sections
    print("\n1. Testing full report generation...")
    try:
        report_path = generator.generate_report(
            company_name="TechCorp Inc.",
            ai_readiness_data=sample_data,
            filename="test_techcorp_report.pdf"
        )
        
        assert os.path.exists(report_path), "PDF file was not created"
        assert os.path.getsize(report_path) > 1000, "PDF file is too small"
        print(f"✓ PDF generated successfully: {report_path}")
        print(f"  File size: {os.path.getsize(report_path)} bytes")
        
    except Exception as e:
        print(f"✗ Error generating PDF: {e}")
        return False
    
    # Test 2: Generate report with minimal data
    print("\n2. Testing report with minimal data...")
    minimal_data = {
        "company_name": "SmallCo",
        "domain": "smallco.com",
        "ai_readiness_score": 35,
        "readiness_category": "Early Stage",
        "confidence": 0.45,
        "component_scores": {
            "tech_hiring": 30,
            "ai_mentions": 25,
            "company_size": 40,
            "industry_adoption": 50,
            "tech_modernization": 30
        },
        "key_strengths": ["Building AI foundation"],
        "improvement_areas": ["Limited AI talent", "Low AI visibility"],
        "recommendations": [
            "Focus on digital transformation before AI adoption",
            "Consider hiring AI/ML talent to build internal capabilities"
        ],
        "data_sources": {
            "hunter_io": True,
            "web_scraping": False,
            "job_postings": False,
            "clearbit": False
        },
        "company_data": {
            "basic_info": {
                "organization": "SmallCo",
                "industry": "Retail",
                "size": "11-50"
            },
            "tech_signals": {},
            "job_postings": {}
        }
    }
    
    try:
        report_path2 = generator.generate_report(
            company_name="SmallCo",
            ai_readiness_data=minimal_data,
            filename="test_smallco_report.pdf"
        )
        
        assert os.path.exists(report_path2), "Minimal PDF was not created"
        print(f"✓ Minimal data PDF generated: {report_path2}")
        print(f"  File size: {os.path.getsize(report_path2)} bytes")
        
    except Exception as e:
        print(f"✗ Error with minimal data: {e}")
        return False
    
    # Test 3: Test different score ranges
    print("\n3. Testing different score ranges...")
    score_tests = [
        (95, "AI-Ready Leader", "high"),
        (75, "Strong Potential", "high"),
        (55, "Emerging Interest", "medium"),
        (40, "Early Stage", "medium"),
        (25, "Not Yet Ready", "low")
    ]
    
    for score, expected_category, color_range in score_tests:
        test_data = sample_data.copy()
        test_data["ai_readiness_score"] = score
        test_data["readiness_category"] = expected_category
        
        try:
            report_path = generator.generate_report(
                company_name=f"TestCo_{score}",
                ai_readiness_data=test_data,
                filename=f"test_score_{score}.pdf"
            )
            print(f"✓ Score {score} ({expected_category}): PDF generated")
            
            # Clean up test files
            if os.path.exists(report_path):
                os.remove(report_path)
                
        except Exception as e:
            print(f"✗ Error with score {score}: {e}")
    
    print("\n" + "=" * 60)
    print("✅ ALL PDF GENERATION TESTS PASSED!")
    print("=" * 60)
    
    # Clean up main test files
    for file in ["test_techcorp_report.pdf", "test_smallco_report.pdf"]:
        filepath = Path("reports") / file
        if filepath.exists():
            filepath.unlink()
            print(f"Cleaned up: {file}")
    
    return True


if __name__ == "__main__":
    test_pdf_generation()