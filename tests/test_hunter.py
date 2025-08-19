"""
Test Hunter.io service and API integration
"""

import sys
from pathlib import Path
import asyncio

sys.path.append(str(Path(__file__).parent.parent / "src"))

from services.hunter_service import HunterService
from fastapi.testclient import TestClient
from main import app


async def test_hunter_service():
    """Test Hunter.io service with mock data"""
    
    print("Testing Hunter.io service...")
    
    # Initialize service (will use mock data without API key)
    service = HunterService()
    
    # Test 1: Search known company
    print("\n1. Testing Google...")
    google = await service.search_domain("google.com")
    assert google is not None
    assert google.organization == "Google"
    assert google.company_size == "10000+"
    assert len(google.technologies) > 0
    print(f"✓ Found: {google.organization}")
    print(f"  Size: {google.company_size}")
    print(f"  Technologies: {', '.join(google.technologies[:3])}...")
    print(f"  Contacts: {len(google.contacts)} executives found")
    
    # Test 2: Test ModelML (AI company)
    print("\n2. Testing ModelML...")
    modelml = await service.search_domain("modelml.com")
    assert modelml is not None
    assert modelml.organization == "ModelML"
    assert "Artificial Intelligence" in modelml.company_industry
    assert "TensorFlow" in modelml.technologies
    print(f"✓ Found: {modelml.organization}")
    print(f"  Industry: {modelml.company_industry}")
    print(f"  Key contacts: {[c['name'] for c in modelml.contacts[:2]]}")
    
    # Test 3: Financial services company
    print("\n3. Testing JPMorgan...")
    jpmorgan = await service.search_domain("jpmorgan.com")
    assert jpmorgan is not None
    assert jpmorgan.organization == "JPMorgan Chase"
    assert jpmorgan.company_industry == "Banking"
    print(f"✓ Found: {jpmorgan.organization}")
    print(f"  Industry: {jpmorgan.company_industry}")
    print(f"  Location: {jpmorgan.city}, {jpmorgan.state}")
    
    # Test 4: Unknown company
    print("\n4. Testing unknown company...")
    unknown = await service.search_domain("unknowncompany456.com")
    assert unknown is None
    print("✓ Unknown company returns None as expected")
    
    # Test 5: Get contacts
    print("\n5. Testing contact search...")
    contacts = await service.find_contacts("modelml.com", department="executive")
    assert len(contacts) > 0
    print(f"✓ Found {len(contacts)} executive contacts")
    
    # Test 6: Account info
    print("\n6. Testing account info...")
    account = service.get_account_info()
    assert account is not None
    print(f"✓ Account status: {account}")
    
    print("\n✅ All Hunter.io service tests passed!")
    return True


def test_api_with_hunter():
    """Test FastAPI integration with Hunter.io"""
    
    print("\n\nTesting API with Hunter.io integration...")
    
    client = TestClient(app)
    
    # Test 1: Analyze with Hunter.io data
    print("\n1. Testing ModelML analysis...")
    response = client.post(
        "/analyze",
        json={"name": "ModelML", "domain": "modelml.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "ModelML"
    assert data["ai_readiness_score"] > 70  # AI company should score high
    assert "Hunter.io" in data["message"]
    assert data["company_data"]["technologies"] is not None
    print(f"✓ ModelML Score: {data['ai_readiness_score']}")
    print(f"  Technologies: {data['company_data']['technologies'][:3]}")
    print(f"  Key contacts: {len(data['company_data']['key_contacts'])} found")
    
    # Test 2: Financial services company
    print("\n2. Testing Goldman Sachs analysis...")
    response = client.post(
        "/analyze",
        json={"name": "Goldman Sachs", "domain": "goldmansachs.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ai_readiness_score"] > 60  # Large financial should score well
    print(f"✓ Goldman Sachs Score: {data['ai_readiness_score']}")
    print(f"  Industry: {data['company_data']['industry']}")
    
    # Test 3: Check account endpoint
    print("\n3. Testing account info endpoint...")
    response = client.get("/api/account")
    assert response.status_code == 200
    data = response.json()
    assert "hunter_io" in data
    print(f"✓ Account info: {data['hunter_io']}")
    
    print("\n✅ All API + Hunter.io integration tests passed!")


if __name__ == "__main__":
    # Run async tests
    asyncio.run(test_hunter_service())
    
    # Run API tests
    test_api_with_hunter()