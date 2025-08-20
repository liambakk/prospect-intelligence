#!/usr/bin/env python3
"""
Test script for company autocomplete and validation functionality
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_suggestions(query):
    """Test company suggestions endpoint"""
    print(f"\n🔍 Testing suggestions for query: '{query}'")
    response = requests.get(f"{BASE_URL}/api/company-suggestions", params={"q": query})
    if response.status_code == 200:
        data = response.json()
        suggestions = data.get("suggestions", [])
        print(f"✅ Found {len(suggestions)} suggestions:")
        for s in suggestions[:5]:
            ticker = f" ({s.get('ticker')})" if s.get('ticker') else ""
            print(f"   - {s['name']}{ticker} - {s.get('type', 'Unknown')}")
    else:
        print(f"❌ Error: {response.status_code}")
    return response.status_code == 200

def test_validation(company_name, expected_valid=True):
    """Test company validation endpoint"""
    print(f"\n🔍 Testing validation for: '{company_name}'")
    response = requests.get(f"{BASE_URL}/api/validate-company", params={"name": company_name})
    if response.status_code == 200:
        data = response.json()
        is_valid = data.get("valid", False)
        if is_valid == expected_valid:
            print(f"✅ Validation correct: {'Valid' if is_valid else 'Invalid'}")
            if not is_valid and data.get("suggestions"):
                print(f"   Suggestions: {', '.join(data['suggestions'])}")
        else:
            print(f"❌ Validation incorrect: Expected {'valid' if expected_valid else 'invalid'}, got {'valid' if is_valid else 'invalid'}")
        return is_valid == expected_valid
    else:
        print(f"❌ Error: {response.status_code}")
        return False

def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("COMPANY AUTOCOMPLETE & VALIDATION TESTS")
    print("=" * 60)
    
    passed = 0
    total = 0
    
    # Test suggestions with various queries
    test_cases_suggestions = [
        "jp",      # Should find JPMorgan Chase
        "gold",    # Should find Goldman Sachs
        "black",   # Should find BlackRock, Blackstone
        "citi",    # Should find Citigroup
        "bank",    # Should find multiple banks
        "tech",    # Should find tech companies if any
        "xyz",     # Should return few or no results
    ]
    
    for query in test_cases_suggestions:
        total += 1
        if test_suggestions(query):
            passed += 1
    
    # Test validation with real and fake companies
    test_cases_validation = [
        ("JPMorgan Chase", True),
        ("Goldman Sachs", True),
        ("BlackRock", True),
        ("Bank of America", True),
        ("Citigroup", True),
        ("FakeCompany123", False),
        ("NotARealBank", False),
        ("TestCorp", False),
        ("My Imaginary Company", False),
    ]
    
    for company, expected in test_cases_validation:
        total += 1
        if test_validation(company, expected):
            passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {total - passed} tests failed")
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    try:
        # Check if server is running
        response = requests.get(BASE_URL, timeout=2)
        print(f"✅ Server is running at {BASE_URL}")
    except requests.exceptions.RequestException:
        print(f"❌ Server is not running at {BASE_URL}")
        print("Please start the Flask app first: python3 app.py")
        sys.exit(1)
    
    success = run_tests()
    sys.exit(0 if success else 1)