from flask import Flask, render_template, request, jsonify, send_file
import json
import time
from datetime import datetime
import os

# Import services
from services.clearbit_service import ClearbitService
from services.job_scraper import JobScraper
from services.news_collector import NewsCollector
from services.website_scraper import WebsiteScraper
from scoring.readiness_scorer import ReadinessScorer
from scoring.recommendation_engine import RecommendationEngine
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize services
clearbit_service = ClearbitService(Config.CLEARBIT_API_KEY)
job_scraper = JobScraper()
news_collector = NewsCollector(Config.NEWS_API_KEY)
website_scraper = WebsiteScraper()
readiness_scorer = ReadinessScorer()
recommendation_engine = RecommendationEngine()

@app.route('/')
def index():
    """Render the main dashboard"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_company():
    """Main endpoint for company analysis"""
    try:
        data = request.json
        company_name = data.get('company_name', '').strip()
        
        if not company_name:
            return jsonify({'error': 'Company name is required'}), 400
        
        # Initialize response
        response = {
            'company_name': company_name,
            'status': 'processing',
            'steps': []
        }
        
        # Step 1: Company Enrichment
        response['steps'].append({'step': 'Fetching company information', 'status': 'complete'})
        company_info = clearbit_service.enrich_company(company_name)
        
        # Step 2: Job Analysis
        response['steps'].append({'step': 'Analyzing job postings', 'status': 'complete'})
        job_analysis = job_scraper.analyze_job_postings(company_name)
        
        # Step 3: News Analysis
        response['steps'].append({'step': 'Collecting recent news', 'status': 'complete'})
        news_analysis = news_collector.get_recent_news(company_name)
        
        # Step 4: Website Analysis
        response['steps'].append({'step': 'Analyzing company website', 'status': 'complete'})
        domain = company_info.get('domain', f"{company_name.lower().replace(' ', '')}.com")
        website_analysis = website_scraper.analyze_website(domain)
        
        # Compile all data
        company_data = {
            'company_info': company_info,
            'job_analysis': job_analysis,
            'news_analysis': news_analysis,
            'website_analysis': website_analysis
        }
        
        # Step 5: Calculate AI Readiness Score
        response['steps'].append({'step': 'Calculating AI readiness score', 'status': 'complete'})
        readiness_score = readiness_scorer.calculate_ai_readiness_score(company_data)
        
        # Step 6: Generate Recommendations
        response['steps'].append({'step': 'Generating sales recommendations', 'status': 'complete'})
        recommendations = recommendation_engine.generate_sales_approach(company_data, readiness_score)
        
        # Compile final response
        response['status'] = 'complete'
        response['company_info'] = company_info
        response['readiness_score'] = readiness_score
        response['recommendations'] = recommendations
        response['job_analysis'] = job_analysis
        response['news_analysis'] = news_analysis
        response['website_analysis'] = website_analysis
        response['timestamp'] = datetime.now().isoformat()
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """Generate PDF report for analysis"""
    try:
        data = request.json
        
        # Import PDF generator (we'll create this next)
        from reports.pdf_generator import PDFGenerator
        
        pdf_gen = PDFGenerator()
        pdf_path = pdf_gen.generate_report(data)
        
        return send_file(pdf_path, as_attachment=True, 
                        download_name=f"{data['company_name']}_AI_Readiness_Report.pdf")
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test_companies')
def test_companies():
    """Endpoint to get test company suggestions"""
    test_companies = [
        {'name': 'JPMorgan Chase', 'expected': 'Very High'},
        {'name': 'Goldman Sachs', 'expected': 'High'},
        {'name': 'BlackRock', 'expected': 'High'}
    ]
    return jsonify(test_companies)

if __name__ == '__main__':
    app.run(debug=True, port=5000)