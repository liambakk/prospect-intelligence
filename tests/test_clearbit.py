"""
Test Clearbit service functionality
"""

import sys
from pathlib import Path
import asyncio

sys.path.append(str(Path(__file__).parent.parent / "src"))

from services.clearbit_service import ClearbitService, ClearbitCompanyData


async def test_clearbit_service():
    """Test Clearbit service with mock data"""
    
    print("Testing Clearbit service...")
    
    # Initialize service (will use mock data without API key)
    service = ClearbitService()
    
    # Test 1: Fetch known company
    print("\n1. Testing known company (google.com)...")
    company = await service.get_company_data("google.com")
    assert company is not None
    assert company.name == "Google"
    assert company.domain == "google.com"
    assert company.employee_count == 150000
    print(f"✓ Found: {company.name} with {company.employee_count} employees")
    
    # Test 2: Cache hit
    print("\n2. Testing cache hit...")
    company2 = await service.get_company_data("google.com")
    assert company2 is not None
    assert company2.name == "Google"
    print("✓ Cache working correctly")
    
    # Test 3: Different company
    print("\n3. Testing ModelML...")
    modelml = await service.get_company_data("modelml.com")
    assert modelml is not None
    assert modelml.name == "ModelML"
    assert modelml.industry == "AI/ML Technology"
    print(f"✓ Found: {modelml.name} - {modelml.description}")
    
    # Test 4: Unknown company returns None
    print("\n4. Testing unknown company...")
    unknown = await service.get_company_data("unknowncompany123.com")
    assert unknown is None
    print("✓ Unknown company correctly returns None")
    
    # Test 5: Domain normalization
    print("\n5. Testing domain normalization...")
    stripe1 = await service.get_company_data("https://stripe.com/payments")
    stripe2 = await service.get_company_data("STRIPE.COM")
    assert stripe1 is not None
    assert stripe2 is not None
    assert stripe1.name == stripe2.name == "Stripe"
    print("✓ Domain normalization working")
    
    # Test 6: Cache stats
    print("\n6. Testing cache stats...")
    stats = service.get_cache_stats()
    print(f"  Cache entries: {stats['entries']}, domains: {stats['domains']}")
    # Should have cached the successful lookups
    assert stats["entries"] > 0
    assert "google.com" in stats["domains"]
    print(f"✓ Cache has {stats['entries']} entries")
    
    print("\n✅ All Clearbit service tests passed!")
    return True


if __name__ == "__main__":
    asyncio.run(test_clearbit_service())