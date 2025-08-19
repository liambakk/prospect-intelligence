"""
Test script for database models
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from database import SessionLocal, init_db
from models import Company, TechSignal, AIReadinessScore, CompanySizeCategory, SignalType


def test_database_models():
    """Test creating and querying database models"""
    
    # Initialize database
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        print("Testing database models...")
        
        # 1. Create a Company
        company = Company(
            name="ModelML",
            domain="modelml.com",
            industry="AI/ML Technology",
            size_category=CompanySizeCategory.STARTUP,
            headquarters="San Francisco, CA",
            employee_count=50,
            revenue_range="$1M-$10M",
            description="AI platform for model deployment and management"
        )
        db.add(company)
        db.commit()
        print(f"✓ Created company: {company.name} (ID: {company.id})")
        
        # 2. Create TechSignals for the company
        tech_signal1 = TechSignal(
            company_id=company.id,
            signal_type=SignalType.JOB_POSTING,
            content="Looking for Senior ML Engineer with experience in LLMs and RAG systems",
            source="LinkedIn",
            source_url="https://linkedin.com/jobs/123",
            date=datetime.now(),
            relevance_score=85,
            ai_mentioned=3,
            tech_keywords=["LLM", "RAG", "Python", "TensorFlow"]
        )
        db.add(tech_signal1)
        
        tech_signal2 = TechSignal(
            company_id=company.id,
            signal_type=SignalType.NEWS_MENTION,
            content="ModelML raises $10M Series A to expand AI platform",
            source="TechCrunch",
            date=datetime.now(),
            relevance_score=90,
            ai_mentioned=5
        )
        db.add(tech_signal2)
        db.commit()
        print(f"✓ Created {len([tech_signal1, tech_signal2])} tech signals")
        
        # 3. Create AIReadinessScore
        ai_score = AIReadinessScore(
            company_id=company.id,
            overall_score=78,
            confidence=0.85,
            component_scores={
                "tech_hires": 85,
                "ai_mentions": 75,
                "company_size": 60,
                "industry_adoption": 90,
                "modernization_signals": 80
            },
            analysis_summary="ModelML shows strong AI readiness with recent hiring and funding",
            recommendations=["Focus on enterprise features", "Expand ML team"],
            decision_makers=[
                {"name": "John Doe", "title": "CTO", "linkedin": "linkedin.com/in/johndoe"},
                {"name": "Jane Smith", "title": "VP Engineering"}
            ],
            data_sources_used=["LinkedIn", "TechCrunch", "Company Website"]
        )
        db.add(ai_score)
        db.commit()
        print(f"✓ Created AI readiness score: {ai_score.overall_score} ({ai_score.readiness_category})")
        
        # 4. Test relationships
        # Query company with its related data
        company_with_data = db.query(Company).filter_by(domain="modelml.com").first()
        print(f"\n✓ Testing relationships:")
        print(f"  - Company has {len(company_with_data.tech_signals)} tech signals")
        print(f"  - Company has {len(company_with_data.ai_readiness_scores)} AI readiness scores")
        
        # 5. Test querying
        high_relevance_signals = db.query(TechSignal).filter(
            TechSignal.relevance_score >= 80
        ).all()
        print(f"  - Found {len(high_relevance_signals)} high relevance signals (score >= 80)")
        
        # 6. Test JSON fields
        latest_score = company_with_data.ai_readiness_scores[0]
        print(f"\n✓ Testing JSON fields:")
        print(f"  - Component scores: {json.dumps(latest_score.component_scores, indent=2)}")
        print(f"  - Is high potential: {latest_score.is_high_potential}")
        
        print("\n✅ All model tests passed successfully!")
        
        # Cleanup - remove test data
        db.query(AIReadinessScore).delete()
        db.query(TechSignal).delete()
        db.query(Company).delete()
        db.commit()
        print("✓ Test data cleaned up")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    test_database_models()