"""
Integration test for FastAPI with database
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, init_db
from models import Company
import json

# Create test client
client = TestClient(app)

def test_fastapi_database_integration():
    """Test that FastAPI can work with the database"""
    
    print("Testing FastAPI + Database integration...")
    
    # Initialize database
    init_db()
    
    # Test 1: Health check
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ Health check passed")
    
    # Test 2: Analyze endpoint
    response = client.post(
        "/analyze",
        json={"name": "TestCompany", "domain": "test.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "TestCompany"
    assert 0 <= data["ai_readiness_score"] <= 100
    assert 0 <= data["confidence"] <= 1
    print("✓ Analyze endpoint works")
    
    # Test 3: Database connectivity from FastAPI context
    db = SessionLocal()
    try:
        # Create a test company
        test_company = Company(
            name="Integration Test Co",
            domain="integrationtest.com",
            industry="Technology"
        )
        db.add(test_company)
        db.commit()
        
        # Query it back
        company = db.query(Company).filter_by(domain="integrationtest.com").first()
        assert company is not None
        assert company.name == "Integration Test Co"
        print("✓ Database operations work from FastAPI context")
        
        # Cleanup
        db.delete(company)
        db.commit()
        print("✓ Test data cleaned up")
        
    finally:
        db.close()
    
    # Test 4: API docs endpoint
    response = client.get("/api/docs")
    assert response.status_code == 200
    assert "endpoints" in response.json()
    print("✓ API documentation endpoint works")
    
    print("\n✅ All integration tests passed!")
    return True

if __name__ == "__main__":
    test_fastapi_database_integration()