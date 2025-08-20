"""
PDF Report Generation Module for Prospect Intelligence Tool
Creates professional PDF reports with AI readiness assessments
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image, KeepTogether
from reportlab.platypus.flowables import HRFlowable
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import os
from pathlib import Path
import io

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """
    Generates professional PDF reports for AI readiness assessments
    """
    
    # ModelML Brand Colors
    COLORS = {
        'primary': HexColor('#1E3A8A'),      # Deep Blue
        'secondary': HexColor('#3B82F6'),    # Bright Blue
        'accent': HexColor('#10B981'),       # Green
        'warning': HexColor('#F59E0B'),      # Orange
        'danger': HexColor('#EF4444'),       # Red
        'dark': HexColor('#1F2937'),         # Dark Gray
        'light': HexColor('#F3F4F6'),        # Light Gray
        'white': HexColor('#FFFFFF'),
        'success': HexColor('#10B981'),      # Green
    }
    
    # Score color ranges
    SCORE_COLORS = {
        'high': HexColor('#10B981'),     # Green (67-100)
        'medium': HexColor('#F59E0B'),   # Yellow/Orange (34-66)
        'low': HexColor('#EF4444')       # Red (0-33)
    }
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize PDF generator
        
        Args:
            output_dir: Directory to save PDF reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.styles = self._create_custom_styles()
    
    def _create_custom_styles(self) -> Dict[str, ParagraphStyle]:
        """Create custom paragraph styles for the report"""
        styles = getSampleStyleSheet()
        custom_styles = {}
        
        # Title style
        custom_styles['CustomTitle'] = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=self.COLORS['primary'],
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Heading 1
        custom_styles['CustomHeading1'] = ParagraphStyle(
            'CustomHeading1',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=self.COLORS['primary'],
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Heading 2
        custom_styles['CustomHeading2'] = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=self.COLORS['dark'],
            spaceAfter=6,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Body text
        custom_styles['CustomBodyText'] = ParagraphStyle(
            'CustomBodyText',
            parent=styles['BodyText'],
            fontSize=10,
            textColor=self.COLORS['dark'],
            alignment=TA_JUSTIFY,
            spaceAfter=6
        )
        
        # Score style (large, centered)
        custom_styles['ScoreStyle'] = ParagraphStyle(
            'ScoreStyle',
            fontSize=36,
            textColor=self.COLORS['primary'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Executive summary
        custom_styles['ExecutiveSummary'] = ParagraphStyle(
            'ExecutiveSummary',
            fontSize=11,
            textColor=self.COLORS['dark'],
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=14
        )
        
        return custom_styles
    
    def generate_report(
        self,
        company_name: str,
        ai_readiness_data: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """
        Generate a comprehensive PDF report
        
        Args:
            company_name: Name of the company
            ai_readiness_data: Complete AI readiness assessment data
            filename: Optional custom filename
        
        Returns:
            Path to the generated PDF file
        """
        try:
            # Generate filename
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_company_name}_AI_Readiness_{timestamp}.pdf"
            
            filepath = self.output_dir / filename
            
            # Create the PDF document
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build the content
            story = []
            
            # Add header
            story.extend(self._create_header(company_name))
            
            # Add executive summary
            story.extend(self._create_executive_summary(ai_readiness_data))
            
            # Add score visualization
            story.extend(self._create_score_section(ai_readiness_data))
            
            # Add company overview
            story.extend(self._create_company_overview(company_name, ai_readiness_data))
            
            # Add technology signals
            story.extend(self._create_tech_signals_section(ai_readiness_data))
            
            # Add job posting analysis (if available)
            if ai_readiness_data.get('company_data', {}).get('job_postings'):
                story.extend(self._create_job_posting_section(ai_readiness_data))
            
            # Add recommendations
            story.extend(self._create_recommendations_section(ai_readiness_data))
            
            # Add data sources
            story.extend(self._create_data_sources_section(ai_readiness_data))
            
            # Add footer
            story.extend(self._create_footer())
            
            # Build the PDF
            doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
            
            logger.info(f"PDF report generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise
    
    def _create_header(self, company_name: str) -> List:
        """Create report header with ModelML branding"""
        elements = []
        
        # Title
        title = Paragraph(
            f"<b>AI Readiness Assessment Report</b>",
            self.styles['CustomTitle']
        )
        elements.append(title)
        
        # Company name
        company = Paragraph(
            f"<b>{company_name}</b>",
            self.styles['CustomHeading1']
        )
        elements.append(company)
        
        # Date
        date_str = datetime.now().strftime("%B %d, %Y")
        date_para = Paragraph(
            f"Generated: {date_str}",
            self.styles['CustomBodyText']
        )
        elements.append(date_para)
        
        # ModelML branding
        branding = Paragraph(
            "<b>Powered by ModelML Prospect Intelligence</b>",
            ParagraphStyle(
                'Branding',
                fontSize=10,
                textColor=self.COLORS['secondary'],
                alignment=TA_CENTER,
                spaceAfter=12
            )
        )
        elements.append(branding)
        
        # Horizontal line
        elements.append(HRFlowable(width="100%", thickness=2, color=self.COLORS['primary']))
        elements.append(Spacer(1, 0.25*inch))
        
        return elements
    
    def _create_executive_summary(self, data: Dict[str, Any]) -> List:
        """Create executive summary section"""
        elements = []
        
        # Section heading
        heading = Paragraph("<b>Executive Summary</b>", self.styles['CustomHeading1'])
        elements.append(heading)
        
        # Get key metrics
        score = data.get('ai_readiness_score', 0)
        category = data.get('readiness_category', 'Not Yet Ready')
        confidence = data.get('confidence', 0)
        
        # Determine summary message based on score
        if score >= 80:
            summary_text = f"{data.get('company_name', 'The company')} demonstrates <b>exceptional AI readiness</b> with a score of {score}/100. They are well-positioned to leverage advanced AI solutions like ModelML's platform immediately."
        elif score >= 65:
            summary_text = f"{data.get('company_name', 'The company')} shows <b>strong potential for AI adoption</b> with a score of {score}/100. With targeted improvements, they can maximize AI value creation."
        elif score >= 50:
            summary_text = f"{data.get('company_name', 'The company')} displays <b>emerging interest in AI</b> with a score of {score}/100. They would benefit from a phased AI adoption approach."
        elif score >= 35:
            summary_text = f"{data.get('company_name', 'The company')} is in the <b>early stages of AI readiness</b> with a score of {score}/100. Foundation building is recommended before major AI initiatives."
        else:
            summary_text = f"{data.get('company_name', 'The company')} currently has <b>limited AI readiness</b> with a score of {score}/100. Digital transformation should precede AI adoption."
        
        summary = Paragraph(summary_text, self.styles['ExecutiveSummary'])
        elements.append(summary)
        
        # Key findings table
        findings_data = [
            ['Key Metric', 'Value'],
            ['AI Readiness Score', f"{score}/100"],
            ['Readiness Category', category],
            ['Assessment Confidence', f"{confidence:.0%}"],
            ['Primary Strength', data.get('key_strengths', ['N/A'])[0] if data.get('key_strengths') else 'Building foundation'],
            ['Primary Gap', data.get('improvement_areas', ['N/A'])[0] if data.get('improvement_areas') else 'Continue journey']
        ]
        
        findings_table = Table(findings_data, colWidths=[2.5*inch, 2.5*inch])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['white']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), self.COLORS['light']),
            ('GRID', (0, 0), (-1, -1), 1, self.COLORS['dark']),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(Spacer(1, 0.2*inch))
        elements.append(findings_table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_score_section(self, data: Dict[str, Any]) -> List:
        """Create score visualization section with charts"""
        elements = []
        
        # Section heading
        heading = Paragraph("<b>AI Readiness Score Analysis</b>", self.styles['CustomHeading1'])
        elements.append(heading)
        
        score = data.get('ai_readiness_score', 0)
        
        # Determine color based on score
        if score >= 67:
            score_color = self.SCORE_COLORS['high']
        elif score >= 34:
            score_color = self.SCORE_COLORS['medium']
        else:
            score_color = self.SCORE_COLORS['low']
        
        # Create score display
        score_text = Paragraph(
            f"<font color='{score_color.hexval()}'>{score}</font>/100",
            self.styles['ScoreStyle']
        )
        elements.append(score_text)
        
        # Category
        category = data.get('readiness_category', 'Not Yet Ready')
        category_para = Paragraph(
            f"<b>{category}</b>",
            ParagraphStyle(
                'Category',
                fontSize=16,
                textColor=score_color,
                alignment=TA_CENTER,
                spaceAfter=20
            )
        )
        elements.append(category_para)
        
        # Component scores breakdown
        if data.get('component_scores'):
            elements.append(Paragraph("<b>Component Scores Breakdown</b>", self.styles['CustomHeading2']))
            
            # Create bar chart for component scores
            drawing = self._create_component_scores_chart(data['component_scores'])
            elements.append(drawing)
            
            # Component scores table
            comp_data = [['Component', 'Score', 'Weight', 'Impact']]
            weights = {
                'tech_hiring': '25%',
                'ai_mentions': '25%',
                'company_size': '20%',
                'industry_adoption': '15%',
                'tech_modernization': '15%'
            }
            
            for comp, score_val in data['component_scores'].items():
                readable_name = comp.replace('_', ' ').title()
                weight = weights.get(comp, '0%')
                impact = f"{float(weight.strip('%')) * score_val / 100:.1f}"
                comp_data.append([readable_name, f"{score_val}/100", weight, impact])
            
            comp_table = Table(comp_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch])
            comp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['secondary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['white']),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            elements.append(Spacer(1, 0.2*inch))
            elements.append(comp_table)
        
        elements.append(Spacer(1, 0.3*inch))
        return elements
    
    def _create_component_scores_chart(self, component_scores: Dict[str, int]) -> Drawing:
        """Create a bar chart for component scores"""
        drawing = Drawing(400, 200)
        
        # Create bar chart
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 125
        bc.width = 300
        bc.data = [[score for score in component_scores.values()]]
        
        # Set categories
        bc.categoryAxis.categoryNames = [
            name.replace('_', ' ').title()[:15]  # Truncate long names
            for name in component_scores.keys()
        ]
        
        # Style the chart
        bc.bars[0].fillColor = self.COLORS['secondary']
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = 100
        bc.valueAxis.valueStep = 20
        bc.categoryAxis.labels.angle = 30
        bc.categoryAxis.labels.fontSize = 8
        bc.valueAxis.labels.fontSize = 8
        
        drawing.add(bc)
        return drawing
    
    def _create_company_overview(self, company_name: str, data: Dict[str, Any]) -> List:
        """Create company overview section"""
        elements = []
        
        heading = Paragraph("<b>Company Overview</b>", self.styles['CustomHeading1'])
        elements.append(heading)
        
        # Extract company data
        company_data = data.get('company_data', {})
        basic_info = company_data.get('basic_info', {})
        
        # Company information table
        overview_data = [
            ['Company', company_name],
            ['Domain', data.get('domain', 'N/A')],
            ['Industry', basic_info.get('industry', 'N/A')],
            ['Company Size', basic_info.get('size', 'N/A')],
            ['Location', basic_info.get('location', 'N/A')],
            ['Data Sources Used', ', '.join([k for k, v in data.get('data_sources', {}).items() if v])]
        ]
        
        overview_table = Table(overview_data, colWidths=[2*inch, 3.5*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.COLORS['light']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(overview_table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_tech_signals_section(self, data: Dict[str, Any]) -> List:
        """Create technology signals section"""
        elements = []
        
        heading = Paragraph("<b>Technology Signals & Indicators</b>", self.styles['CustomHeading1'])
        elements.append(heading)
        
        tech_signals = data.get('company_data', {}).get('tech_signals', {})
        
        # AI mentions
        ai_mentions = tech_signals.get('ai_mentions', 0)
        ai_text = f"• <b>AI/ML Mentions on Website:</b> {ai_mentions} occurrences"
        elements.append(Paragraph(ai_text, self.styles['CustomBodyText']))
        
        # Tech stack
        tech_stack = tech_signals.get('tech_stack', [])
        if tech_stack:
            stack_text = f"• <b>Detected Technology Stack:</b> {', '.join(tech_stack[:10])}"
            elements.append(Paragraph(stack_text, self.styles['CustomBodyText']))
        
        # AI roles hiring
        ai_roles = tech_signals.get('ai_roles_hiring', [])
        if ai_roles:
            roles_text = f"• <b>AI/ML Roles Currently Hiring:</b> {', '.join(ai_roles[:5])}"
            elements.append(Paragraph(roles_text, self.styles['CustomBodyText']))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _create_job_posting_section(self, data: Dict[str, Any]) -> List:
        """Create job posting analysis section"""
        elements = []
        
        job_data = data.get('company_data', {}).get('job_postings', {})
        
        if job_data.get('total_jobs', 0) > 0:
            heading = Paragraph("<b>Hiring & Talent Acquisition Analysis</b>", self.styles['CustomHeading1'])
            elements.append(heading)
            
            # Job statistics table
            job_stats = [
                ['Metric', 'Value'],
                ['Total Job Postings', str(job_data.get('total_jobs', 0))],
                ['AI/ML Specific Roles', str(job_data.get('ai_ml_jobs', 0))],
                ['General Tech Roles', str(job_data.get('tech_jobs', 0))],
                ['AI Hiring Intensity', job_data.get('ai_hiring_intensity', 'none').title()]
            ]
            
            job_table = Table(job_stats, colWidths=[2.5*inch, 2*inch])
            job_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['secondary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['white']),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(job_table)
            
            # Top AI technologies from job postings
            top_tech = job_data.get('top_ai_technologies', [])
            if top_tech:
                elements.append(Spacer(1, 0.1*inch))
                tech_heading = Paragraph("<b>Top AI/ML Technologies in Demand:</b>", self.styles['CustomHeading2'])
                elements.append(tech_heading)
                
                for tech in top_tech[:5]:
                    tech_text = f"• {tech.get('keyword', 'N/A').title()} ({tech.get('count', 0)} mentions)"
                    elements.append(Paragraph(tech_text, self.styles['CustomBodyText']))
            
            elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_recommendations_section(self, data: Dict[str, Any]) -> List:
        """Create recommendations section"""
        elements = []
        
        heading = Paragraph("<b>Strategic Recommendations</b>", self.styles['CustomHeading1'])
        elements.append(heading)
        
        recommendations = data.get('recommendations', [])
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                rec_text = f"<b>{i}.</b> {rec}"
                rec_para = Paragraph(rec_text, self.styles['CustomBodyText'])
                elements.append(rec_para)
                elements.append(Spacer(1, 0.1*inch))
        else:
            no_rec = Paragraph("No specific recommendations at this time.", self.styles['CustomBodyText'])
            elements.append(no_rec)
        
        # Add ModelML value proposition
        elements.append(Spacer(1, 0.2*inch))
        value_prop = Paragraph(
            "<b>How ModelML Can Help:</b>",
            self.styles['CustomHeading2']
        )
        elements.append(value_prop)
        
        score = data.get('ai_readiness_score', 0)
        if score >= 70:
            modelml_text = "Your organization is ready for advanced AI implementation. ModelML's platform can help you scale AI initiatives rapidly with enterprise-grade infrastructure and proven AI models."
        elif score >= 50:
            modelml_text = "ModelML can accelerate your AI journey with guided implementation, pre-built models, and expert support to ensure successful AI adoption."
        else:
            modelml_text = "ModelML offers foundational AI workshops and consulting to help build your organization's AI capabilities and create a roadmap for successful adoption."
        
        modelml_para = Paragraph(modelml_text, self.styles['CustomBodyText'])
        elements.append(modelml_para)
        
        elements.append(Spacer(1, 0.3*inch))
        return elements
    
    def _create_data_sources_section(self, data: Dict[str, Any]) -> List:
        """Create data sources and confidence section"""
        elements = []
        
        heading = Paragraph("<b>Assessment Methodology & Data Sources</b>", self.styles['CustomHeading2'])
        elements.append(heading)
        
        sources = data.get('data_sources', {})
        confidence = data.get('confidence', 0)
        
        # Data sources used
        sources_text = "This assessment utilized the following data sources:"
        elements.append(Paragraph(sources_text, self.styles['CustomBodyText']))
        
        source_list = []
        if sources.get('hunter_io'):
            source_list.append("• Hunter.io - Company and contact information")
        if sources.get('web_scraping'):
            source_list.append("• Web Scraping - Technology signals and AI mentions")
        if sources.get('job_postings'):
            source_list.append("• Job Postings - Hiring patterns and skill requirements")
        if sources.get('clearbit'):
            source_list.append("• Clearbit - Company enrichment data")
        
        for source in source_list:
            elements.append(Paragraph(source, self.styles['CustomBodyText']))
        
        # Confidence level
        elements.append(Spacer(1, 0.1*inch))
        conf_text = f"<b>Assessment Confidence Level:</b> {confidence:.0%}"
        elements.append(Paragraph(conf_text, self.styles['CustomBodyText']))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _create_footer(self) -> List:
        """Create report footer"""
        elements = []
        
        # Separator
        elements.append(HRFlowable(width="100%", thickness=1, color=self.COLORS['primary']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Disclaimer
        disclaimer_text = (
            "<i>This report is generated automatically based on publicly available data and "
            "AI-powered analysis. Results should be validated with additional research and "
            "direct company engagement. ModelML Prospect Intelligence Tool - Demo Version.</i>"
        )
        disclaimer = Paragraph(
            disclaimer_text,
            ParagraphStyle(
                'Disclaimer',
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        elements.append(disclaimer)
        
        # Contact info
        contact = Paragraph(
            "<b>ModelML</b> | AI Solutions for Enterprise | www.modelml.com",
            ParagraphStyle(
                'Contact',
                fontSize=9,
                textColor=self.COLORS['secondary'],
                alignment=TA_CENTER,
                spaceAfter=12
            )
        )
        elements.append(Spacer(1, 0.1*inch))
        elements.append(contact)
        
        return elements
    
    def _add_page_number(self, canvas, doc):
        """Add page numbers to each page"""
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.grey)
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawRightString(doc.pagesize[0] - 72, 40, text)
        canvas.restoreState()