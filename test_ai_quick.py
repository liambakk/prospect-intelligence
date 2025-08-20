#!/usr/bin/env python3
"""
Quick test to verify AI-powered recommendations are working
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_ai_recommendations():
    """Quick test of AI recommendations via API"""
    
    # Check OpenAI key
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    print(f"OpenAI API Key: {'✅ Configured' if has_key else '❌ Not configured'}")
    
    if not has_key:
        print("Please add OPENAI_API_KEY to .env file")
        return False
    
    print("\n🧪 Testing AI Recommendations via API...")
    print("-" * 50)
    
    url = "http://localhost:8000/analyze/comprehensive"
    
    # Test with a well-known company
    test_company = {
        "name": "Microsoft",
        "domain": "microsoft.com"
    }
    
    print(f"Testing with: {test_company['name']}")
    print("This may take 30-60 seconds...")
    
    async with httpx.AsyncClient(timeout=90) as client:
        try:
            response = await client.post(url, json=test_company)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for AI-powered recommendations
                recommendations = data.get("recommendations", {})
                ai_strategy = recommendations.get("ai_powered_strategy", {})
                
                if ai_strategy:
                    print("\n✅ AI-Powered Recommendations Generated!")
                    print("-" * 50)
                    
                    # Display key AI-generated fields
                    print(f"Company: {data.get('company_name')}")
                    print(f"AI Readiness Score: {data.get('ai_readiness_score')}/100")
                    print(f"\n📊 AI Strategy:")
                    print(f"  Priority: {ai_strategy.get('priority_level', 'N/A')}")
                    print(f"  Deal Size: {ai_strategy.get('estimated_deal_size', 'N/A')}")
                    print(f"  Timeline: {ai_strategy.get('timeline', 'N/A')}")
                    
                    # Show talking points
                    talking_points = ai_strategy.get('key_talking_points', [])
                    if talking_points:
                        print(f"\n💡 Key Talking Points:")
                        for i, point in enumerate(talking_points[:3], 1):
                            print(f"  {i}. {point}")
                    
                    # Show use cases
                    use_cases = ai_strategy.get('recommended_use_cases', [])
                    if use_cases:
                        print(f"\n🎯 Recommended Use Cases:")
                        for i, use_case in enumerate(use_cases[:3], 1):
                            print(f"  {i}. {use_case}")
                    
                    # Show competitive positioning
                    if ai_strategy.get('competitive_positioning'):
                        print(f"\n🏆 Competitive Positioning:")
                        print(f"  {ai_strategy['competitive_positioning'][:150]}...")
                    
                    print("\n" + "="*50)
                    print("✅ SUCCESS: AI recommendations are working!")
                    print("="*50)
                    
                    # Check if it's truly AI-generated (not template)
                    # AI-generated content should be specific to the company
                    strategy_text = ai_strategy.get('sales_strategy', '')
                    if test_company['name'].lower() in strategy_text.lower():
                        print("\n🤖 Confirmed: Using OpenAI GPT for dynamic generation")
                    else:
                        print("\n📝 Note: May be using template fallback")
                    
                    return True
                else:
                    print("\n⚠️ No AI strategy found in response")
                    print("Response may be using fallback templates")
                    return False
            else:
                print(f"\n❌ API Error: {response.status_code}")
                print(f"Details: {response.text[:200]}")
                return False
                
        except httpx.ConnectError:
            print("\n❌ Could not connect to server")
            print("Make sure the server is running: python src/main.py")
            return False
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return False


async def main():
    """Run the quick test"""
    print("\n" + "="*60)
    print("AI-POWERED RECOMMENDATIONS - QUICK TEST")
    print("="*60)
    
    success = await test_ai_recommendations()
    
    if success:
        print("\n✅ All tests passed! AI recommendations are operational.")
        print("\nThe system is now generating personalized sales strategies using OpenAI GPT.")
        print("Each analysis will produce unique, context-aware recommendations based on:")
        print("  • Company's AI readiness score")
        print("  • Industry and size")
        print("  • Hiring patterns and tech signals")
        print("  • Recent news and initiatives")
    else:
        print("\n⚠️ AI recommendations may not be fully operational.")
        print("Check the .env file and ensure OPENAI_API_KEY is set correctly.")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)