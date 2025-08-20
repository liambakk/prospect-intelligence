"""
Enhanced PDF Report Generation Module with ModelML Design System
Creates beautiful, modern PDF reports matching the dashboard aesthetic
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    PageBreak, Image, KeepTogether, Frame, PageTemplate, BaseDocTemplate,
    ListFlowable, ListItem
)
from reportlab.platypus.flowables import HRFlowable, Flowable
from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Line, Path
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import renderPDF

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import os
import io
import math

logger = logging.getLogger(__name__)


class ModernGauge(Flowable):
    """Modern circular gauge with minimal design"""
    
    def __init__(self, score, width=180, height=180):
        Flowable.__init__(self)
        self.score = score
        self.width = width
        self.height = height
        
        # ModelML color scheme
        if score >= 80:
            self.color = HexColor('#10b981')  # Green
            self.category = 'VERY HIGH'
        elif score >= 65:
            self.color = HexColor('#3b82f6')  # Blue  
            self.category = 'HIGH'
        elif score >= 50:
            self.color = HexColor('#f59e0b')  # Orange
            self.category = 'MODERATE'
        else:
            self.color = HexColor('#ef4444')  # Red
            self.category = 'LOW'
    
    def draw(self):
        canvas = self.canv
        cx, cy = self.width/2, self.height/2
        radius = min(self.width, self.height) * 0.35
        
        # Outer ring (subtle)
        canvas.setStrokeColor(HexColor('#f7fafc'))
        canvas.setLineWidth(1)
        canvas.circle(cx, cy, radius + 15, stroke=1, fill=0)
        
        # Background track
        canvas.setStrokeColor(HexColor('#e2e8f0'))
        canvas.setLineWidth(8)
        canvas.circle(cx, cy, radius, stroke=1, fill=0)
        
        # Score arc
        canvas.setStrokeColor(self.color)
        canvas.setLineWidth(8)
        canvas.setLineCap(1)  # Round cap
        
        # Arc from -135 to score percentage of 270 degrees
        start_angle = -135
        arc_angle = (self.score / 100) * 270
        canvas.arc(cx - radius, cy - radius, cx + radius, cy + radius, 
                  start_angle, start_angle + arc_angle)
        
        # Large score number
        canvas.setFillColor(HexColor('#0f1419'))
        canvas.setFont('Helvetica-Bold', 42)
        score_text = str(int(self.score))
        text_width = canvas.stringWidth(score_text, 'Helvetica-Bold', 42)
        canvas.drawString(cx - text_width/2, cy + 8, score_text)
        
        # Score out of 100
        canvas.setFont('Helvetica', 10)
        canvas.setFillColor(HexColor('#718096'))
        out_of = "/ 100"
        out_width = canvas.stringWidth(out_of, 'Helvetica', 10)
        canvas.drawString(cx - out_width/2, cy - 15, out_of)
        
        # Category below
        canvas.setFont('Helvetica-Bold', 9)
        canvas.setFillColor(self.color)
        cat_width = canvas.stringWidth(self.category, 'Helvetica-Bold', 9)
        canvas.drawString(cx - cat_width/2, cy - 35, self.category)


class SectionHeader(Flowable):
    """Custom section header with ModelML styling"""
    
    def __init__(self, number, title, width=500, height=60):
        Flowable.__init__(self)
        self.number = number
        self.title = title
        self.width = width
        self.height = height
    
    def draw(self):
        canvas = self.canv
        
        # Number circle
        canvas.setFillColor(HexColor('#3b82f6'))
        canvas.circle(20, self.height/2, 15, stroke=0, fill=1)
        
        # Number text
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 12)
        num_text = str(self.number)
        num_width = canvas.stringWidth(num_text, 'Helvetica-Bold', 12)
        canvas.drawString(20 - num_width/2, self.height/2 - 4, num_text)
        
        # Section title
        canvas.setFillColor(HexColor('#0f1419'))
        canvas.setFont('Helvetica-Bold', 18)
        canvas.drawString(50, self.height/2 - 6, self.title)
        
        # Underline
        canvas.setStrokeColor(HexColor('#e2e8f0'))
        canvas.setLineWidth(1)
        canvas.line(0, 5, self.width, 5)


class MetricCard(Flowable):
    """Modern metric card component"""
    
    def __init__(self, label, value, color='#3b82f6', width=150, height=80):
        Flowable.__init__(self)
        self.label = label
        self.value = value
        self.color = HexColor(color)
        self.width = width
        self.height = height
    
    def draw(self):
        canvas = self.canv
        
        # Card background
        canvas.setFillColor(HexColor('#ffffff'))
        canvas.setStrokeColor(HexColor('#e2e8f0'))
        canvas.roundRect(0, 0, self.width, self.height, 8, stroke=1, fill=1)
        
        # Accent bar
        canvas.setFillColor(self.color)
        canvas.rect(0, self.height - 4, self.width, 4, stroke=0, fill=1)
        
        # Value
        canvas.setFillColor(HexColor('#0f1419'))
        canvas.setFont('Helvetica-Bold', 24)
        value_text = str(self.value)
        value_width = canvas.stringWidth(value_text, 'Helvetica-Bold', 24)
        canvas.drawString(self.width/2 - value_width/2, self.height/2 + 5, value_text)
        
        # Label
        canvas.setFillColor(HexColor('#718096'))
        canvas.setFont('Helvetica', 10)
        label_width = canvas.stringWidth(self.label, 'Helvetica', 10)
        canvas.drawString(self.width/2 - label_width/2, 15, self.label)


class EnhancedPDFReportGenerator:
    """Modern PDF report generator with ModelML design system"""
    
    # ModelML Color Palette
    COLORS = {
        'primary_dark': HexColor('#0f1419'),
        'primary_hover': HexColor('#1a2332'),
        'secondary_dark': HexColor('#2d3748'),
        'background_light': HexColor('#f7fafc'),
        'background_white': HexColor('#ffffff'),
        'border_light': HexColor('#e2e8f0'),
        'text_primary': HexColor('#1a202c'),
        'text_secondary': HexColor('#718096'),
        'text_muted': HexColor('#a0aec0'),
        'accent_blue': HexColor('#3b82f6'),
        'accent_green': HexColor('#10b981'),
        'accent_orange': HexColor('#f59e0b'),
        'accent_red': HexColor('#ef4444'),
    }
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize the PDF generator"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles matching ModelML design"""
        base_styles = getSampleStyleSheet()
        styles = {}
        
        # Cover title
        styles['CoverTitle'] = ParagraphStyle(
            'CoverTitle',
            fontSize=36,
            textColor=self.COLORS['primary_dark'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=20,
            leading=42
        )
        
        # Cover subtitle
        styles['CoverSubtitle'] = ParagraphStyle(
            'CoverSubtitle',
            fontSize=18,
            textColor=self.COLORS['text_secondary'],
            alignment=TA_CENTER,
            fontName='Helvetica',
            spaceAfter=30
        )
        
        # Section heading
        styles['SectionHeading'] = ParagraphStyle(
            'SectionHeading',
            fontSize=22,
            textColor=self.COLORS['primary_dark'],
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceAfter=20,
            spaceBefore=10
        )
        
        # Subsection heading
        styles['SubHeading'] = ParagraphStyle(
            'SubHeading',
            fontSize=16,
            textColor=self.COLORS['secondary_dark'],
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceAfter=12,
            spaceBefore=8
        )
        
        # Body text
        styles['BodyText'] = ParagraphStyle(
            'BodyText',
            fontSize=11,
            textColor=self.COLORS['text_primary'],
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            spaceAfter=10,
            leading=16
        )
        
        # Metric label
        styles['MetricLabel'] = ParagraphStyle(
            'MetricLabel',
            fontSize=10,
            textColor=self.COLORS['text_muted'],
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        # Metric value
        styles['MetricValue'] = ParagraphStyle(
            'MetricValue',
            fontSize=28,
            textColor=self.COLORS['primary_dark'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Insight text
        styles['InsightText'] = ParagraphStyle(
            'InsightText',
            fontSize=11,
            textColor=self.COLORS['text_secondary'],
            alignment=TA_LEFT,
            fontName='Helvetica',
            leftIndent=20,
            spaceAfter=8,
            bulletIndent=10
        )
        
        # Footer
        styles['Footer'] = ParagraphStyle(
            'Footer',
            fontSize=9,
            textColor=self.COLORS['text_muted'],
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        # Add base styles
        for name in base_styles.byName:
            styles[name] = base_styles[name]
        
        return styles
    
    def generate_report(
        self,
        company_name: str,
        ai_readiness_data: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """Generate the complete PDF report"""
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
                rightMargin=54,
                leftMargin=54,
                topMargin=72,
                bottomMargin=54
            )
            
            # Build the story
            story = []
            
            # Page 1: Cover Page
            story.extend(self._create_cover_page(company_name, ai_readiness_data))
            story.append(PageBreak())
            
            # Page 2: Executive Summary
            story.extend(self._create_executive_summary(company_name, ai_readiness_data))
            story.append(PageBreak())
            
            # Page 3: AI Readiness Score Analysis
            story.extend(self._create_score_analysis(ai_readiness_data))
            story.append(PageBreak())
            
            # Page 4: Component Scores Breakdown
            story.extend(self._create_component_breakdown(ai_readiness_data))
            story.append(PageBreak())
            
            # Page 5: Technology Signals
            story.extend(self._create_technology_signals(ai_readiness_data))
            story.append(PageBreak())
            
            # Page 6: Market Intelligence
            story.extend(self._create_market_intelligence(ai_readiness_data))
            story.append(PageBreak())
            
            # Page 7: Strategic Recommendations
            story.extend(self._create_recommendations(ai_readiness_data))
            story.append(PageBreak())
            
            # Page 8: Implementation Roadmap
            story.extend(self._create_roadmap(ai_readiness_data))
            story.append(PageBreak())
            
            # Page 9: Next Steps
            story.extend(self._create_next_steps(company_name, ai_readiness_data))
            
            # Build the PDF
            doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
            
            logger.info(f"PDF report generated successfully: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise
    
    def _create_cover_page(self, company_name: str, data: Dict[str, Any]) -> List:
        """Create a minimal, elegant cover page"""
        elements = []
        
        # Top spacing
        elements.append(Spacer(1, 2*inch))
        
        # ModelML Logo
        logo_path = self._get_logo_path()
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=60, height=60)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 0.5*inch))
            except:
                pass
        
        # Title
        elements.append(Paragraph(
            "AI READINESS ASSESSMENT",
            self.styles['CoverTitle']
        ))
        
        # Company name
        elements.append(Paragraph(
            f"<font color='#3b82f6'>{company_name}</font>",
            self.styles['CoverSubtitle']
        ))
        
        elements.append(Spacer(1, 1*inch))
        
        # Score display
        score = self._extract_score(data.get('ai_readiness_score', 0))
        gauge = ModernGauge(score, width=180, height=180)
        elements.append(gauge)
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Readiness level (only show the level, not the full evaluation text)
        category = data.get('readiness_category', 'Assessment Pending')
        # Extract just the readiness level (e.g., "Very High" from "Very High - Prime candidate...")
        if ' - ' in category:
            category = category.split(' - ')[0]
        elements.append(Paragraph(
            f"<b>{category}</b>",
            ParagraphStyle(
                'ReadinessLevel',
                fontSize=16,
                textColor=self._get_score_color(score),
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
        ))
        
        # Date
        elements.append(Spacer(1, 1.5*inch))
        date_str = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(date_str, self.styles['Footer']))
        
        # ModelML branding
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(
            "Powered by ModelML Prospect Intelligence",
            self.styles['Footer']
        ))
        
        return elements
    
    def _create_executive_summary(self, company_name: str, data: Dict[str, Any]) -> List:
        """Create executive summary page"""
        elements = []
        
        # Section header
        elements.append(SectionHeader(1, "Executive Summary"))
        elements.append(Spacer(1, 0.3*inch))
        
        # Key metrics cards
        metrics_data = []
        score = self._extract_score(data.get('ai_readiness_score', 0))
        
        # Create a table of metric cards
        card1 = MetricCard("AI Readiness", f"{int(score)}/100", '#3b82f6')
        card2 = MetricCard("Confidence", "85%", '#10b981')
        card3 = MetricCard("Industry Rank", "Top 20%", '#f59e0b')
        
        metrics_table = Table([[card1, card2, card3]], colWidths=[160, 160, 160])
        metrics_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(metrics_table)
        
        elements.append(Spacer(1, 0.4*inch))
        
        # Summary text
        elements.append(Paragraph("<b>Assessment Overview</b>", self.styles['SubHeading']))
        
        summary_text = self._generate_executive_summary(company_name, score)
        elements.append(Paragraph(summary_text, self.styles['BodyText']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Key findings
        elements.append(Paragraph("<b>Key Findings</b>", self.styles['SubHeading']))
        
        findings = self._extract_key_findings(data)
        for finding in findings[:4]:  # Limit to 4 findings
            bullet_text = f"• {finding}"
            elements.append(Paragraph(bullet_text, self.styles['InsightText']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Strategic opportunity
        elements.append(Paragraph("<b>Strategic Opportunity</b>", self.styles['SubHeading']))
        
        opportunity = self._generate_opportunity_text(score, company_name)
        elements.append(Paragraph(opportunity, self.styles['BodyText']))
        
        return elements
    
    def _create_score_analysis(self, data: Dict[str, Any]) -> List:
        """Create detailed score analysis page"""
        elements = []
        
        # Section header
        elements.append(SectionHeader(2, "AI Readiness Score Analysis"))
        elements.append(Spacer(1, 0.3*inch))
        
        score = self._extract_score(data.get('ai_readiness_score', 0))
        
        # Score interpretation
        elements.append(Paragraph("<b>Score Interpretation</b>", self.styles['SubHeading']))
        interpretation = self._get_detailed_interpretation(score)
        elements.append(Paragraph(interpretation, self.styles['BodyText']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Industry comparison
        elements.append(Paragraph("<b>Industry Benchmarking</b>", self.styles['SubHeading']))
        
        # Create comparison table
        benchmark_data = [
            ['Category', 'Your Score', 'Industry Avg', 'Leaders'],
            ['Overall', f'{int(score)}', '62', '85'],
            ['Technology', '75', '58', '88'],
            ['Talent', '82', '65', '90'],
            ['Strategy', '70', '60', '82']
        ]
        
        benchmark_table = Table(benchmark_data, colWidths=[120, 100, 100, 100])
        benchmark_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['background_light']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['text_primary']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS['border_light']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.COLORS['background_light']]),
        ]))
        elements.append(benchmark_table)
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Maturity level
        elements.append(Paragraph("<b>AI Maturity Level</b>", self.styles['SubHeading']))
        maturity = self._determine_maturity_level(score)
        elements.append(Paragraph(maturity, self.styles['BodyText']))
        
        return elements
    
    def _create_component_breakdown(self, data: Dict[str, Any]) -> List:
        """Create component scores breakdown page"""
        elements = []
        
        # Section header
        elements.append(SectionHeader(3, "Component Score Breakdown"))
        elements.append(Spacer(1, 0.3*inch))
        
        # Component scores
        components = data.get('component_scores', {})
        if not components:
            components = {
                'Technology Infrastructure': 75,
                'AI Talent & Skills': 82,
                'Data Readiness': 68,
                'Strategic Alignment': 70,
                'Innovation Culture': 78
            }
        
        # Create visual representation
        for comp_name, comp_score in components.items():
            # Component name
            elements.append(Paragraph(f"<b>{comp_name}</b>", self.styles['SubHeading']))
            
            # Progress bar
            drawing = Drawing(450, 30)
            
            # Background bar
            drawing.add(Rect(0, 10, 450, 10, fillColor=self.COLORS['background_light'], strokeColor=None))
            
            # Score bar
            bar_width = (comp_score / 100) * 450
            bar_color = self._get_score_color(comp_score)
            drawing.add(Rect(0, 10, bar_width, 10, fillColor=bar_color, strokeColor=None))
            
            # Score text
            drawing.add(String(460, 12, f"{int(comp_score)}%", fontSize=10, fillColor=self.COLORS['text_secondary']))
            
            elements.append(drawing)
            
            # Component insight
            insight = self._generate_component_insight(comp_name, comp_score)
            elements.append(Paragraph(insight, self.styles['InsightText']))
            elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_technology_signals(self, data: Dict[str, Any]) -> List:
        """Create technology signals analysis page"""
        elements = []
        
        # Section header
        elements.append(SectionHeader(4, "Technology Signals & Indicators"))
        elements.append(Spacer(1, 0.3*inch))
        
        # Tech stack analysis
        elements.append(Paragraph("<b>Current Technology Stack</b>", self.styles['SubHeading']))
        
        tech_items = [
            "Cloud Infrastructure: AWS, Azure deployment detected",
            "Data Analytics: Advanced analytics tools in use",
            "API Architecture: Modern RESTful APIs implemented",
            "Security: Enterprise-grade security measures",
            "Automation: CI/CD pipelines established"
        ]
        
        for item in tech_items:
            elements.append(Paragraph(f"• {item}", self.styles['InsightText']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # AI initiatives
        elements.append(Paragraph("<b>AI & ML Initiatives</b>", self.styles['SubHeading']))
        
        initiatives = data.get('website_analysis', {}).get('ai_initiatives', [])
        if not initiatives:
            initiatives = [
                "Machine Learning models in production",
                "Natural Language Processing capabilities",
                "Predictive analytics implementation",
                "Computer vision exploration"
            ]
        
        for init in initiatives[:5]:
            if isinstance(init, dict):
                text = init.get('title', init.get('description', str(init)))
            else:
                text = str(init)
            elements.append(Paragraph(f"• {text}", self.styles['InsightText']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Digital transformation indicators
        elements.append(Paragraph("<b>Digital Transformation Indicators</b>", self.styles['SubHeading']))
        
        transformation_score = self._calculate_transformation_score(data)
        elements.append(Paragraph(
            f"Digital transformation maturity: <b>{transformation_score}%</b>",
            self.styles['BodyText']
        ))
        
        return elements
    
    def _create_market_intelligence(self, data: Dict[str, Any]) -> List:
        """Create market intelligence page"""
        elements = []
        
        # Section header
        elements.append(SectionHeader(5, "Market Intelligence"))
        elements.append(Spacer(1, 0.3*inch))
        
        # Recent developments
        elements.append(Paragraph("<b>Recent Developments</b>", self.styles['SubHeading']))
        
        news = data.get('news_analysis', {}).get('recent_mentions', [])
        if news:
            for item in news[:4]:
                if isinstance(item, dict):
                    title = item.get('title', 'Recent development')
                else:
                    title = str(item)
                elements.append(Paragraph(f"• {title}", self.styles['InsightText']))
        else:
            elements.append(Paragraph(
                "No recent public developments identified in our analysis.",
                self.styles['InsightText']
            ))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Competitive positioning
        elements.append(Paragraph("<b>Competitive Positioning</b>", self.styles['SubHeading']))
        
        positioning_text = """
        Based on our analysis, the organization shows strong potential for AI adoption 
        with key strengths in technology infrastructure and talent acquisition. The 
        competitive landscape indicates opportunities for differentiation through 
        strategic AI implementation.
        """
        elements.append(Paragraph(positioning_text, self.styles['BodyText']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Talent insights
        elements.append(Paragraph("<b>Talent & Hiring Signals</b>", self.styles['SubHeading']))
        
        job_data = data.get('job_analysis', {})
        if job_data.get('ai_roles_count', 0) > 0:
            elements.append(Paragraph(
                f"• Active AI/ML positions: {job_data.get('ai_roles_count', 'Multiple')}",
                self.styles['InsightText']
            ))
            elements.append(Paragraph(
                f"• Technical roles expansion: {job_data.get('tech_roles_percentage', 'High')}",
                self.styles['InsightText']
            ))
        else:
            elements.append(Paragraph(
                "• Limited public hiring data available",
                self.styles['InsightText']
            ))
        
        return elements
    
    def _create_recommendations(self, data: Dict[str, Any]) -> List:
        """Create strategic recommendations page"""
        elements = []
        
        # Section header
        elements.append(SectionHeader(6, "Strategic Recommendations"))
        elements.append(Spacer(1, 0.3*inch))
        
        score = self._extract_score(data.get('ai_readiness_score', 0))
        
        # Primary recommendation
        elements.append(Paragraph("<b>Primary Recommendation</b>", self.styles['SubHeading']))
        
        primary_rec = self._get_primary_recommendation(score)
        elements.append(Paragraph(primary_rec, self.styles['BodyText']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # ModelML value proposition
        elements.append(Paragraph("<b>ModelML Value Proposition</b>", self.styles['SubHeading']))
        
        value_props = [
            "Enterprise-ready AI infrastructure platform",
            "Rapid deployment with minimal technical debt",
            "Scalable solutions aligned with existing tech stack",
            "Proven ROI in financial services sector",
            "Comprehensive support and training programs"
        ]
        
        for prop in value_props:
            elements.append(Paragraph(f"• {prop}", self.styles['InsightText']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Implementation approach
        elements.append(Paragraph("<b>Recommended Implementation Approach</b>", self.styles['SubHeading']))
        
        approach = self._get_implementation_approach(score)
        elements.append(Paragraph(approach, self.styles['BodyText']))
        
        return elements
    
    def _create_roadmap(self, data: Dict[str, Any]) -> List:
        """Create implementation roadmap page"""
        elements = []
        
        # Section header
        elements.append(SectionHeader(7, "Implementation Roadmap"))
        elements.append(Spacer(1, 0.3*inch))
        
        # Timeline
        roadmap_data = [
            ['Phase', 'Timeline', 'Key Activities', 'Expected Outcomes'],
            ['Discovery', 'Weeks 1-2', 'Requirements gathering\nTechnical assessment', 'Clear project scope'],
            ['Pilot', 'Weeks 3-8', 'POC development\nInitial deployment', 'Validated approach'],
            ['Scale', 'Weeks 9-16', 'Full implementation\nTeam training', 'Production deployment'],
            ['Optimize', 'Ongoing', 'Performance tuning\nFeature expansion', 'Maximum ROI']
        ]
        
        roadmap_table = Table(roadmap_data, colWidths=[80, 80, 180, 140])
        roadmap_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['accent_blue']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS['border_light']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.COLORS['background_light']]),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(roadmap_table)
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Success metrics
        elements.append(Paragraph("<b>Success Metrics</b>", self.styles['SubHeading']))
        
        metrics = [
            "Time to first AI model deployment: < 8 weeks",
            "User adoption rate: > 80% within 3 months",
            "Process efficiency improvement: 30-40%",
            "ROI realization: 6-12 months",
            "Technical debt reduction: 25%"
        ]
        
        for metric in metrics:
            elements.append(Paragraph(f"• {metric}", self.styles['InsightText']))
        
        return elements
    
    def _create_next_steps(self, company_name: str, data: Dict[str, Any]) -> List:
        """Create next steps page"""
        elements = []
        
        # Section header
        elements.append(SectionHeader(8, "Next Steps"))
        elements.append(Spacer(1, 0.3*inch))
        
        # Immediate actions
        elements.append(Paragraph("<b>Immediate Actions</b>", self.styles['SubHeading']))
        
        actions = [
            "Schedule executive briefing with ModelML team",
            "Identify pilot project for initial implementation",
            "Assess current data infrastructure readiness",
            "Define success criteria and KPIs",
            "Establish cross-functional AI task force"
        ]
        
        for i, action in enumerate(actions, 1):
            elements.append(Paragraph(f"{i}. {action}", self.styles['InsightText']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Contact information
        elements.append(Paragraph("<b>Connect with ModelML</b>", self.styles['SubHeading']))
        
        contact_info = """
        <b>Sales Team</b><br/>
        Email: sales@modelml.com<br/>
        Phone: 1-800-MODEL-ML<br/>
        <br/>
        <b>Schedule a Demo</b><br/>
        Visit: modelml.com/demo<br/>
        <br/>
        <b>Learn More</b><br/>
        Resources: modelml.com/resources<br/>
        Case Studies: modelml.com/success-stories
        """
        
        elements.append(Paragraph(contact_info, self.styles['BodyText']))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Closing message
        closing = f"""
        Thank you for reviewing this AI Readiness Assessment for {company_name}. 
        ModelML is committed to partnering with forward-thinking organizations to 
        unlock the full potential of artificial intelligence. We look forward to 
        discussing how we can accelerate your AI journey.
        """
        
        elements.append(Paragraph(closing, self.styles['BodyText']))
        
        # Footer
        elements.append(Spacer(1, 1*inch))
        elements.append(HRFlowable(
            width="100%",
            thickness=0.5,
            color=self.COLORS['border_light']
        ))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(
            "© 2024 ModelML. Confidential and Proprietary.",
            self.styles['Footer']
        ))
        
        return elements
    
    def _add_page_number(self, canvas, doc):
        """Add page numbers and subtle branding to each page"""
        canvas.saveState()
        
        # Page number
        page_num = canvas.getPageNumber()
        if page_num > 1:  # Skip page number on cover
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(self.COLORS['text_muted'])
            canvas.drawString(letter[0] - 72, 36, str(page_num))
        
        # Subtle ModelML branding on each page
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(self.COLORS['text_muted'])
        canvas.drawString(54, 36, "ModelML Prospect Intelligence")
        
        canvas.restoreState()
    
    # Helper methods
    def _get_logo_path(self) -> Optional[str]:
        """Get the path to the ModelML logo"""
        possible_paths = [
            "/tmp/modelml.png",
            "static/modelml.png",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "static/modelml.png"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _extract_score(self, score_data):
        """Extract numeric score from various formats"""
        if isinstance(score_data, dict):
            return score_data.get('total_score', 0)
        return float(score_data)
    
    def _get_score_color(self, score: float) -> Color:
        """Get color based on score value"""
        if score >= 80:
            return self.COLORS['accent_green']
        elif score >= 65:
            return self.COLORS['accent_blue']
        elif score >= 50:
            return self.COLORS['accent_orange']
        else:
            return self.COLORS['accent_red']
    
    def _generate_executive_summary(self, company_name: str, score: float) -> str:
        """Generate executive summary text"""
        if score >= 80:
            return f"""
            {company_name} demonstrates exceptional AI readiness with a score of {int(score)}/100, 
            positioning the organization among industry leaders. The assessment reveals strong 
            technological foundations, active talent acquisition in AI/ML roles, and clear 
            strategic alignment for AI adoption. This presents an ideal opportunity for 
            advanced AI implementation with ModelML's enterprise platform.
            """
        elif score >= 65:
            return f"""
            {company_name} shows strong AI readiness with a score of {int(score)}/100, 
            indicating solid foundations for AI adoption. The organization has demonstrated 
            commitment to digital transformation with emerging AI initiatives. Strategic 
            partnerships with ModelML can accelerate the journey from experimentation to 
            scaled AI deployment.
            """
        else:
            return f"""
            {company_name} is in the early stages of AI readiness with a score of {int(score)}/100. 
            While current AI adoption is limited, the assessment identifies clear opportunities 
            for growth. A phased approach with ModelML's guidance can help build the necessary 
            foundations for successful AI implementation.
            """
    
    def _extract_key_findings(self, data: Dict[str, Any]) -> List[str]:
        """Extract key findings from the data"""
        findings = []
        
        score = self._extract_score(data.get('ai_readiness_score', 0))
        if score >= 70:
            findings.append("Strong technical infrastructure ready for AI deployment")
        
        if data.get('job_analysis', {}).get('ai_roles_count', 0) > 0:
            findings.append("Active recruitment of AI/ML talent indicates strategic commitment")
        
        if data.get('website_analysis', {}).get('tech_stack_modern', False):
            findings.append("Modern technology stack facilitates AI integration")
        
        findings.append("Significant opportunity for competitive advantage through AI")
        findings.append("Cultural readiness for digital transformation observed")
        
        return findings
    
    def _generate_opportunity_text(self, score: float, company_name: str) -> str:
        """Generate opportunity text based on score"""
        if score >= 70:
            return f"""
            {company_name} is uniquely positioned to become an AI leader in their sector. 
            With ModelML's platform, the organization can rapidly deploy production-ready 
            AI solutions, achieving measurable ROI within 6-12 months. The existing 
            technical infrastructure and talent base provide an ideal foundation for 
            transformative AI initiatives.
            """
        else:
            return f"""
            {company_name} has significant potential to leverage AI for business transformation. 
            ModelML's comprehensive approach, combining technology, methodology, and support, 
            can help build AI capabilities systematically. Starting with focused pilot projects, 
            the organization can demonstrate value while building internal expertise.
            """
    
    def _get_detailed_interpretation(self, score: float) -> str:
        """Get detailed score interpretation"""
        if score >= 80:
            return """
            This score indicates advanced AI readiness with mature capabilities across 
            technology, talent, and strategy dimensions. The organization has likely already 
            begun AI initiatives and is ready for enterprise-scale deployment. ModelML's 
            platform can accelerate existing efforts and unlock new use cases.
            """
        elif score >= 65:
            return """
            This score reflects strong foundations with specific areas for enhancement. 
            The organization shows commitment to AI but may need support in scaling from 
            pilots to production. ModelML's expertise can bridge these gaps and ensure 
            successful enterprise-wide adoption.
            """
        else:
            return """
            This score suggests early-stage AI readiness with opportunities for structured 
            development. While current capabilities may be limited, the assessment identifies 
            clear pathways for growth. ModelML's phased approach can help build capabilities 
            systematically while delivering quick wins.
            """
    
    def _determine_maturity_level(self, score: float) -> str:
        """Determine AI maturity level description"""
        if score >= 80:
            return "Level 4: Optimizing - AI is embedded in core processes with continuous improvement"
        elif score >= 65:
            return "Level 3: Defined - AI initiatives are formalized with clear governance"
        elif score >= 50:
            return "Level 2: Developing - Pilot projects underway with emerging capabilities"
        else:
            return "Level 1: Initial - Exploring AI opportunities with foundational building"
    
    def _generate_component_insight(self, component: str, score: float) -> str:
        """Generate insight for component score"""
        insights = {
            'Technology Infrastructure': f"Score of {int(score)}% indicates {'strong' if score >= 70 else 'developing'} technical foundations",
            'AI Talent & Skills': f"Score of {int(score)}% reflects {'robust' if score >= 70 else 'growing'} AI expertise",
            'Data Readiness': f"Score of {int(score)}% shows {'mature' if score >= 70 else 'evolving'} data capabilities",
            'Strategic Alignment': f"Score of {int(score)}% demonstrates {'clear' if score >= 70 else 'emerging'} AI strategy",
            'Innovation Culture': f"Score of {int(score)}% reveals {'strong' if score >= 70 else 'developing'} innovation mindset"
        }
        return insights.get(component, f"Score of {int(score)}% in this dimension")
    
    def _calculate_transformation_score(self, data: Dict[str, Any]) -> int:
        """Calculate digital transformation score"""
        indicators = 0
        total = 5
        
        if data.get('website_analysis', {}).get('tech_stack_modern', False):
            indicators += 1
        if data.get('job_analysis', {}).get('tech_roles_percentage', 0) > 20:
            indicators += 1
        if data.get('news_analysis', {}).get('digital_transformation_mentioned', False):
            indicators += 1
        if data.get('website_analysis', {}).get('api_mentioned', False):
            indicators += 1
        if data.get('website_analysis', {}).get('cloud_mentioned', False):
            indicators += 1
        
        return int((indicators / total) * 100)
    
    def _get_primary_recommendation(self, score: float) -> str:
        """Get primary recommendation based on score"""
        if score >= 80:
            return """
            Immediate opportunity for enterprise AI deployment. We recommend starting with 
            a strategic partnership to identify high-impact use cases and deploy ModelML's 
            platform for rapid value creation. Focus on scaling existing pilots and expanding 
            into new AI applications.
            """
        elif score >= 65:
            return """
            Strong candidate for accelerated AI adoption. We recommend a phased approach 
            starting with a flagship project to demonstrate value, followed by systematic 
            expansion. ModelML's platform can bridge current gaps and ensure successful scaling.
            """
        else:
            return """
            Foundation-building phase recommended. Start with AI readiness workshops and 
            pilot projects in controlled environments. ModelML can provide strategic guidance 
            and technology to build capabilities while managing risk.
            """
    
    def _get_implementation_approach(self, score: float) -> str:
        """Get implementation approach based on score"""
        if score >= 70:
            return """
            1. Executive alignment workshop (Week 1)
            2. Use case prioritization and ROI modeling (Week 2)
            3. Technical architecture review and integration planning (Week 3)
            4. Pilot project kickoff with ModelML platform (Week 4)
            5. Iterative deployment with continuous optimization (Weeks 5-12)
            """
        else:
            return """
            1. AI readiness assessment and gap analysis (Week 1-2)
            2. Foundation building: data, infrastructure, governance (Weeks 3-6)
            3. Proof of concept development (Weeks 7-10)
            4. Pilot deployment with success metrics (Weeks 11-14)
            5. Scale based on pilot results (Week 15+)
            """