"""
Test FastAPI integration with Clearbit service
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from main import app
import json

# Create test client
client = TestClient(app)

def test_api_clearbit_integration():
    """Test API with Clearbit integration"""
    
    print("Testing FastAPI + Clearbit integration...")
    
    # Test 1: Analyze with domain
    print("\n1. Testing analysis with domain (google.com)...")
    response = client.post(
        "/analyze",
        json={"name": "Google", "domain": "google.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "Google"
    assert data["domain"] == "google.com"
    assert data["ai_readiness_score"] > 50  # Should have high score
    assert data["confidence"] > 0.5
    assert data["company_data"] is not None
    assert data["company_data"]["employees"] == 150000
    print(f"✓ Google analysis: Score={data['ai_readiness_score']}, Confidence={data['confidence']}")
    print(f"  Company data: {data['company_data']['industry']}, {data['company_data']['employees']} employees")
    
    # Test 2: Analyze ModelML
    print("\n2. Testing ModelML analysis...")
    response = client.post(
        "/analyze",
        json={"name": "ModelML", "domain": "modelml.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "ModelML"
    assert data["ai_readiness_score"] > 60  # AI company should score well
    tech_stack = data["company_data"]["tech_stack"]
    assert "TensorFlow" in tech_stack
    print(f"✓ ModelML analysis: Score={data['ai_readiness_score']}")
    print(f"  Tech stack: {', '.join(tech_stack[:3])}...")
    
    # Test 3: Analyze without domain
    print("\n3. Testing analysis without domain...")
    response = client.post(
        "/analyze",
        json={"name": "Unknown Company"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "Unknown Company"
    assert data["confidence"] < 0.5  # Low confidence without domain
    assert data["company_data"] is None
    print(f"✓ No domain analysis: Score={data['ai_readiness_score']}, Confidence={data['confidence']}")
    
    # Test 4: Unknown domain
    print("\n4. Testing unknown domain...")
    response = client.post(
        "/analyze",
        json={"name": "Fake Corp", "domain": "fakecorp123.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] < 0.5
    print(f"✓ Unknown domain handled: Score={data['ai_readiness_score']}")
    
    print("\n✅ All API + Clearbit integration tests passed!")
    return True

if __name__ == "__main__":
    test_api_clearbit_integration()