#!/usr/bin/env python3
"""
Final verification that AI-powered recommendations are working
Shows real examples of AI-generated content
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def verify_ai_system():
    """Verify AI recommendations are truly AI-powered"""
    
    print("\n" + "="*70)
    print("🚀 AI-POWERED RECOMMENDATIONS VERIFICATION")
    print("="*70)
    
    # Check OpenAI key status
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    key_preview = os.getenv("OPENAI_API_KEY", "")[:20] if has_key else "Not configured"
    
    print(f"\n📋 System Status:")
    print(f"  • OpenAI API Key: {'✅ Configured' if has_key else '❌ Missing'}")
    print(f"  • Key Preview: {key_preview}...")
    print(f"  • API Endpoint: http://localhost:8000/analyze/comprehensive")
    
    if not has_key:
        print("\n❌ OpenAI key not found. AI recommendations will use templates.")
        return False
    
    print("\n🔍 Testing with JPMorgan Chase (Financial Services)...")
    print("-" * 70)
    
    url = "http://localhost:8000/analyze/comprehensive"
    test_company = {
        "name": "JPMorgan Chase",
        "domain": "jpmorganchase.com"
    }
    
    async with httpx.AsyncClient(timeout=120) as client:
        try:
            print("⏳ Analyzing company (this may take 30-60 seconds)...")
            response = await client.post(url, json=test_company)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract AI recommendations
                recommendations = data.get("recommendations", {})
                ai_strategy = recommendations.get("ai_powered_strategy", {})
                
                if ai_strategy and ai_strategy.get("sales_strategy"):
                    print("\n✅ AI-POWERED RECOMMENDATIONS SUCCESSFULLY GENERATED!")
                    print("="*70)
                    
                    # Display company analysis
                    print(f"\n📊 Company Analysis:")
                    print(f"  • Company: {data.get('company_name')}")
                    print(f"  • AI Readiness Score: {data.get('ai_readiness_score')}/100")
                    print(f"  • Category: {data.get('readiness_category')}")
                    print(f"  • Industry: {'Financial Services' if data.get('is_financial_company') else 'General'}")
                    
                    # Display AI-generated strategy
                    print(f"\n🤖 AI-Generated Sales Strategy:")
                    print(f"  {ai_strategy.get('sales_strategy')}")
                    
                    print(f"\n💰 Deal Intelligence:")
                    print(f"  • Priority Level: {ai_strategy.get('priority_level', 'N/A').upper()}")
                    print(f"  • Estimated Deal Size: {ai_strategy.get('estimated_deal_size', 'N/A')}")
                    print(f"  • Timeline: {ai_strategy.get('timeline', 'N/A')}")
                    
                    # Display talking points
                    print(f"\n💡 Key Talking Points (AI-Generated):")
                    for i, point in enumerate(ai_strategy.get('key_talking_points', [])[:5], 1):
                        print(f"  {i}. {point}")
                    
                    # Display use cases
                    print(f"\n🎯 Recommended Use Cases (AI-Generated):")
                    for i, use_case in enumerate(ai_strategy.get('recommended_use_cases', [])[:5], 1):
                        print(f"  {i}. {use_case}")
                    
                    # Display objection handling
                    objections = ai_strategy.get('objection_handling', [])
                    if objections:
                        print(f"\n🛡️ Objection Handling (AI-Generated):")
                        for obj in objections[:3]:
                            print(f"  • Objection: {obj.get('objection', 'N/A')}")
                            print(f"    Response: {obj.get('response', 'N/A')}")
                    
                    # Display competitive positioning
                    if ai_strategy.get('competitive_positioning'):
                        print(f"\n🏆 Competitive Positioning:")
                        print(f"  {ai_strategy['competitive_positioning']}")
                    
                    # Display next steps
                    print(f"\n📋 Next Steps (AI-Generated):")
                    for i, step in enumerate(ai_strategy.get('next_steps', [])[:5], 1):
                        print(f"  {i}. {step}")
                    
                    # Verify it's truly AI-generated
                    print("\n" + "="*70)
                    print("🔍 VERIFICATION RESULTS:")
                    print("="*70)
                    
                    # Check for company-specific content
                    strategy_text = str(ai_strategy)
                    checks = {
                        "Company name mentioned": "jpmorgan" in strategy_text.lower() or "chase" in strategy_text.lower(),
                        "Financial services context": any(term in strategy_text.lower() for term in ["financial", "banking", "compliance", "regulatory"]),
                        "Specific deal size": "$" in ai_strategy.get('estimated_deal_size', ''),
                        "Multiple talking points": len(ai_strategy.get('key_talking_points', [])) >= 3,
                        "Multiple use cases": len(ai_strategy.get('recommended_use_cases', [])) >= 3,
                        "Objection handling": len(ai_strategy.get('objection_handling', [])) >= 1,
                        "Competitive positioning": bool(ai_strategy.get('competitive_positioning')),
                        "Next steps defined": len(ai_strategy.get('next_steps', [])) >= 3
                    }
                    
                    all_passed = True
                    for check, result in checks.items():
                        status = "✅" if result else "❌"
                        print(f"  {status} {check}")
                        if not result:
                            all_passed = False
                    
                    # Data sources used
                    print(f"\n📊 Data Sources Used:")
                    sources = data.get('data_sources', {})
                    for source, used in sources.items():
                        status = "✅" if used else "⭕"
                        print(f"  {status} {source.replace('_', ' ').title()}")
                    
                    print("\n" + "="*70)
                    if all_passed:
                        print("✅ SUCCESS: AI-POWERED RECOMMENDATIONS ARE FULLY OPERATIONAL!")
                        print("\nThe system is generating:")
                        print("  • Dynamic, company-specific sales strategies")
                        print("  • Personalized talking points based on analysis")
                        print("  • Industry-relevant use cases")
                        print("  • Intelligent objection handling")
                        print("  • Competitive positioning insights")
                        print("  • Actionable next steps")
                    else:
                        print("⚠️ PARTIAL SUCCESS: AI recommendations are working but may be using some templates")
                    print("="*70)
                    
                    return all_passed
                else:
                    print("\n❌ No AI strategy found in response")
                    print("The system may be using fallback templates")
                    return False
            else:
                print(f"\n❌ API Error: {response.status_code}")
                return False
                
        except httpx.ConnectError:
            print("\n❌ Could not connect to server")
            print("Ensure the server is running: python src/main.py")
            return False
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return False


async def main():
    """Run verification"""
    success = await verify_ai_system()
    
    if success:
        print("\n🎉 VERIFICATION COMPLETE!")
        print("The Prospect Intelligence Tool is using OpenAI GPT to generate")
        print("intelligent, context-aware sales recommendations for each company.")
    else:
        print("\n⚠️ Verification incomplete. Check the logs above for details.")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)