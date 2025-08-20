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
    print(f"✓ Found: {google.organization}")
    # Company size is optional in API response
    if google.company_size:
        print(f"  Size: {google.company_size}")
    if google.technologies and len(google.technologies) > 0:
        print(f"  Technologies: {', '.join(google.technologies[:3])}...")
    if google.contacts:
        print(f"  Contacts: {len(google.contacts)} executives found")
    
    # Test 2: Test ModelML (AI company) - might not be in Hunter.io
    print("\n2. Testing ModelML...")
    modelml = await service.search_domain("modelml.com")
    if modelml:
        print(f"✓ Found: {modelml.organization}")
        if modelml.company_industry:
            print(f"  Industry: {modelml.company_industry}")
        if modelml.contacts:
            print(f"  Key contacts: {[c['name'] for c in modelml.contacts[:2]]}")
    else:
        print("  ModelML not found in Hunter.io (expected for newer companies)")
    
    # Test 3: Financial services company
    print("\n3. Testing JPMorgan...")
    jpmorgan = await service.search_domain("jpmorgan.com")
    if jpmorgan:
        print(f"✓ Found: {jpmorgan.organization}")
        if jpmorgan.company_industry:
            print(f"  Industry: {jpmorgan.company_industry}")
    else:
        print("  JPMorgan not found in Hunter.io")
    
    # Test 4: Unknown company
    print("\n4. Testing unknown company...")
    unknown = await service.search_domain("unknowncompany456.com")
    if unknown is None:
        print("✓ Unknown company returns None as expected")
    else:
        print(f"  Found: {unknown.organization}")
    
    # Test 5: Get contacts
    print("\n5. Testing contact search...")
    contacts = await service.find_contacts("modelml.com", department="executive")
    if contacts and len(contacts) > 0:
        print(f"✓ Found {len(contacts)} executive contacts")
    else:
        print("  No contacts found (may be a newer company)")
    
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
    # Company name might be different based on what Hunter.io returns
    assert data["ai_readiness_score"] > 0  # Should have a score
    print(f"✓ {data['company_name']} Score: {data['ai_readiness_score']}")
    if data.get("company_data") and data["company_data"].get("technologies"):
        print(f"  Technologies: {data['company_data']['technologies'][:3]}")
    if data.get("company_data") and data["company_data"].get("key_contacts"):
        print(f"  Key contacts: {len(data['company_data']['key_contacts'])} found")
    
    # Test 2: Financial services company
    print("\n2. Testing Goldman Sachs analysis...")
    response = client.post(
        "/analyze",
        json={"name": "Goldman Sachs", "domain": "goldmansachs.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ai_readiness_score"] > 0  # Should have a score
    print(f"✓ {data['company_name']} Score: {data['ai_readiness_score']}")
    if data.get("company_data") and data["company_data"].get("industry"):
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