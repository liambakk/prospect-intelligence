from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
import os

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Create ModelML-inspired custom styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#0a1628'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#0a1628'),
            spaceAfter=12,
            spaceBefore=12,
            leftIndent=0
        ))
        
        # Subheading style
        self.styles.add(ParagraphStyle(
            name='CustomSubheading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e3a5f'),
            spaceAfter=8,
            spaceBefore=8
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#4b5563'),
            alignment=TA_JUSTIFY,
            spaceAfter=8
        ))
        
        # Score style
        self.styles.add(ParagraphStyle(
            name='ScoreStyle',
            parent=self.styles['Title'],
            fontSize=48,
            textColor=colors.HexColor('#3b82f6'),
            alignment=TA_CENTER
        ))
    
    def generate_report(self, data):
        """Generate PDF report from analysis data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data['company_name']}_AI_Readiness_{timestamp}.pdf"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build content
        story = []
        
        # Title Page
        story.append(Paragraph("ModelML Prospect Intelligence Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"AI Readiness Analysis", self.styles['CustomSubheading']))
        story.append(Spacer(1, 0.5*inch))
        
        # Company Name
        story.append(Paragraph(data['company_name'], self.styles['Title']))
        story.append(Spacer(1, 0.3*inch))
        
        # Score Display
        score = data['readiness_score']['total_score']
        story.append(Paragraph(f"{score:.1f}", self.styles['ScoreStyle']))
        story.append(Paragraph(data['readiness_score']['readiness_level'], self.styles['CustomSubheading']))
        story.append(Spacer(1, 0.5*inch))
        
        # Report Date
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal']))
        story.append(PageBreak())
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['CustomHeading']))
        company_info = data['company_info']
        summary_text = f"""
        {company_info['name']} is a {company_info['industry']} company with {company_info['employeeCount']:,} employees 
        based in {company_info['location']['city']}, {company_info['location']['state']}. 
        Our analysis indicates an AI readiness score of {score:.1f}/100, categorizing them as "{data['readiness_score']['readiness_level']}".
        """
        story.append(Paragraph(summary_text, self.styles['CustomBody']))
        story.append(Spacer(1, 0.3*inch))
        
        # Component Scores
        story.append(Paragraph("AI Readiness Components", self.styles['CustomHeading']))
        component_data = [['Component', 'Score']]
        for key, value in data['readiness_score']['component_scores'].items():
            label = key.replace('_', ' ').title()
            component_data.append([label, f"{value:.0f}/100"])
        
        component_table = Table(component_data, colWidths=[3*inch, 1.5*inch])
        component_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0a1628')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
        ]))
        story.append(component_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Key Findings
        story.append(Paragraph("Key Findings", self.styles['CustomHeading']))
        
        # Job Analysis
        job_data = data['job_analysis']
        story.append(Paragraph("Technical Hiring Activity", self.styles['CustomSubheading']))
        job_text = f"""
        {company_info['name']} currently has {job_data['ai_ml_positions']} AI/ML positions open out of 
        {job_data['total_open_positions']} total job openings, indicating a {job_data['growth_indicator']} 
        level of AI talent acquisition.
        """
        story.append(Paragraph(job_text, self.styles['CustomBody']))
        story.append(Spacer(1, 0.2*inch))
        
        # Recent Initiatives
        news_data = data['news_analysis']
        if news_data['recent_initiatives']:
            story.append(Paragraph("Recent AI Initiatives", self.styles['CustomSubheading']))
            for initiative in news_data['recent_initiatives'][:3]:
                initiative_text = f"• {initiative['title']} ({initiative['date']})"
                story.append(Paragraph(initiative_text, self.styles['CustomBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Decision Makers
        story.append(PageBreak())
        story.append(Paragraph("Key Decision Makers", self.styles['CustomHeading']))
        for dm in data['recommendations']['decision_makers']:
            dm_text = f"""
            <b>{dm['name']}</b><br/>
            {dm['title']}<br/>
            <i>Approach: {dm['approach']}</i>
            """
            story.append(Paragraph(dm_text, self.styles['CustomBody']))
            story.append(Spacer(1, 0.15*inch))
        
        # Sales Approach
        story.append(Paragraph("Recommended Sales Approach", self.styles['CustomHeading']))
        approach = data['recommendations']['sales_approach']
        story.append(Paragraph(f"Strategy: {approach['strategy']}", self.styles['CustomSubheading']))
        story.append(Paragraph(approach['messaging'], self.styles['CustomBody']))
        story.append(Spacer(1, 0.2*inch))
        
        # Next Steps
        story.append(Paragraph("Recommended Next Steps", self.styles['CustomSubheading']))
        for step in data['recommendations']['next_steps']:
            story.append(Paragraph(f"• {step}", self.styles['CustomBody']))
        
        # Data Sources
        story.append(PageBreak())
        story.append(Paragraph("Data Sources & Methodology", self.styles['CustomHeading']))
        methodology_text = """
        This report was generated using ModelML's Prospect Intelligence system, which analyzes multiple data sources including:
        company information databases, job posting platforms, news articles, and company websites. The AI readiness score is 
        calculated using a weighted algorithm considering technical hiring, AI mentions, company growth, industry benchmarks, 
        and technology modernization indicators.
        """
        story.append(Paragraph(methodology_text, self.styles['CustomBody']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"Confidence Level: {data['readiness_score']['confidence']}", self.styles['CustomBody']))
        
        # Build PDF
        doc.build(story)
        
        return filepath