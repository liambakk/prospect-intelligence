#!/usr/bin/env python3
"""
Quick setup verification script for Prospect Intelligence Tool
Run this after setup to verify everything is configured correctly
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_setup():
    """Check if the system is properly configured"""
    print("\n" + "="*60)
    print("🔍 PROSPECT INTELLIGENCE - SETUP VERIFICATION")
    print("="*60)
    
    issues = []
    warnings = []
    
    # Check Python version
    python_version = sys.version_info
    print(f"\n✅ Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
        issues.append("Python 3.9+ is required")
    
    # Check required packages
    print("\n📦 Checking Required Packages:")
    required_packages = [
        "fastapi",
        "uvicorn",
        "httpx",
        "beautifulsoup4",
        "reportlab",
        "python-dotenv",
        "pydantic"
    ]
    
    for package in required_packages:
        try:
            if package == "beautifulsoup4":
                __import__("bs4")
            elif package == "python-dotenv":
                __import__("dotenv")
            else:
                __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            issues.append(f"Missing package: {package}")
            print(f"  ❌ {package}")
    
    # Check API keys
    print("\n🔑 Checking API Keys:")
    
    # Company data (at least one required)
    hunter_key = os.getenv("HUNTER_API_KEY")
    clearbit_key = os.getenv("CLEARBIT_API_KEY")
    
    if hunter_key and hunter_key != "your_hunter_api_key_here":
        print(f"  ✅ Hunter.io API Key: {hunter_key[:10]}...")
    elif clearbit_key and clearbit_key != "your_clearbit_api_key_here":
        print(f"  ✅ Clearbit API Key: {clearbit_key[:10]}...")
    else:
        issues.append("No company data API key found (need Hunter.io or Clearbit)")
        print("  ❌ No company data API (Hunter.io or Clearbit)")
    
    # Job postings (required)
    rapidapi_key = os.getenv("RAPIDAPI_KEY")
    if rapidapi_key and rapidapi_key != "your_rapidapi_key_here":
        print(f"  ✅ RapidAPI Key: {rapidapi_key[:10]}...")
    else:
        issues.append("RapidAPI key not found (required for job postings)")
        print("  ❌ RapidAPI Key (required)")
    
    # News (required)
    news_key = os.getenv("NEWS_API_KEY")
    if news_key and news_key != "your_newsapi_key_here":
        print(f"  ✅ NewsAPI Key: {news_key[:10]}...")
    else:
        issues.append("NewsAPI key not found (required for news analysis)")
        print("  ❌ NewsAPI Key (required)")
    
    # OpenAI (optional but recommended)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key != "your_openai_api_key_here":
        print(f"  ✅ OpenAI API Key: {openai_key[:20]}...")
    else:
        warnings.append("OpenAI key not found (AI recommendations will use templates)")
        print("  ⚠️  OpenAI API Key (optional but recommended)")
    
    # Check directories
    print("\n📁 Checking Directory Structure:")
    required_dirs = ["src", "static", "reports", "src/services"]
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"  ✅ {dir_path}/")
        else:
            issues.append(f"Missing directory: {dir_path}")
            print(f"  ❌ {dir_path}/")
    
    # Check key files
    print("\n📄 Checking Key Files:")
    required_files = [
        "src/main.py",
        "static/index.html",
        "requirements.txt",
        ".env"
    ]
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            if file_path == ".env":
                issues.append(".env file not found - copy .env.example and add your keys")
            else:
                issues.append(f"Missing file: {file_path}")
            print(f"  ❌ {file_path}")
    
    # Summary
    print("\n" + "="*60)
    if issues:
        print("❌ SETUP INCOMPLETE - Issues Found:")
        for issue in issues:
            print(f"  • {issue}")
        print("\nPlease fix these issues before running the application.")
    else:
        print("✅ SETUP COMPLETE - Ready to run!")
        print("\nStart the application with:")
        print("  python src/main.py")
        print("\nThen open http://localhost:8000 in your browser")
    
    if warnings:
        print("\n⚠️  Warnings (optional improvements):")
        for warning in warnings:
            print(f"  • {warning}")
    
    print("="*60)
    
    return len(issues) == 0

if __name__ == "__main__":
    success = check_setup()
    sys.exit(0 if success else 1)