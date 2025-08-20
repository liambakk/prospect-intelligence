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
    PageBreak, Image, KeepTogether, Frame, PageTemplate, BaseDocTemplate
)
from reportlab.platypus.flowables import HRFlowable, Flowable
from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Line
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.widgets.markers import makeMarker
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import os
from pathlib import Path
import io
import math

logger = logging.getLogger(__name__)


class ScoreGauge(Flowable):
    """Custom flowable for circular score gauge matching dashboard design"""
    
    def __init__(self, score, width=200, height=200):
        Flowable.__init__(self)
        self.score = score
        self.width = width
        self.height = height
        
        # Determine color based on score
        if score >= 80:
            self.color = HexColor('#10b981')  # Green
        elif score >= 65:
            self.color = HexColor('#3b82f6')  # Blue
        elif score >= 50:
            self.color = HexColor('#f59e0b')  # Orange
        else:
            self.color = HexColor('#ef4444')  # Red
    
    def draw(self):
        # Draw background circle
        canvas = self.canv
        cx, cy = self.width/2, self.height/2
        radius = min(self.width, self.height) * 0.4
        
        # Background track
        canvas.setStrokeColor(HexColor('#e2e8f0'))
        canvas.setLineWidth(12)
        canvas.circle(cx, cy, radius, stroke=1, fill=0)
        
        # Score arc
        canvas.setStrokeColor(self.color)
        canvas.setLineWidth(12)
        canvas.setLineCap(1)  # Round cap
        
        # Calculate arc based on score (270 degrees total, starting from -135)
        start_angle = -135
        arc_angle = (self.score / 100) * 270
        canvas.arc(cx - radius, cy - radius, cx + radius, cy + radius, 
                  start_angle, start_angle + arc_angle)
        
        # Score text
        canvas.setFillColor(HexColor('#0f1419'))
        canvas.setFont('Helvetica-Bold', 48)
        score_text = str(int(self.score))
        text_width = canvas.stringWidth(score_text, 'Helvetica-Bold', 48)
        canvas.drawString(cx - text_width/2, cy + 10, score_text)
        
        # Category label with dynamic text
        canvas.setFont('Helvetica-Bold', 11)
        canvas.setFillColor(self.color)
        label = self.category
        label_width = canvas.stringWidth(label, 'Helvetica-Bold', 11)
        canvas.drawString(cx - label_width/2, cy - 25, label)


class ModernCard(Flowable):
    """Custom flowable for modern card-style sections"""
    
    def __init__(self, content, width=500, padding=20, background=None, border_color=None):
        Flowable.__init__(self)
        self.content = content
        self.width = width
        self.padding = padding
        self.background = background or HexColor('#ffffff')
        self.border_color = border_color or HexColor('#e2e8f0')
        self.height = 100  # Will be calculated
    
    def draw(self):
        canvas = self.canv
        
        # Draw rounded rectangle background
        canvas.setFillColor(self.background)
        canvas.setStrokeColor(self.border_color)
        canvas.setLineWidth(1)
        canvas.roundRect(0, 0, self.width, self.height, 8, stroke=1, fill=1)


class EnhancedPDFReportGenerator:
    """
    Generates beautiful PDF reports with ModelML design system
    """
    
    # ModelML Design System Colors
    COLORS = {
        'primary_dark': HexColor('#0f1419'),     # Dark navy
        'primary_hover': HexColor('#1a2332'),    # Hover state
        'secondary_dark': HexColor('#2d3748'),   # Secondary dark
        'background_light': HexColor('#f7fafc'), # Light background
        'background_white': HexColor('#ffffff'), # White
        'border_light': HexColor('#e2e8f0'),     # Light border
        'text_primary': HexColor('#1a202c'),     # Primary text
        'text_secondary': HexColor('#718096'),   # Secondary text
        'text_muted': HexColor('#a0aec0'),       # Muted text
        'accent_blue': HexColor('#3b82f6'),      # Blue accent
        'accent_green': HexColor('#10b981'),     # Green accent
        'accent_orange': HexColor('#f59e0b'),    # Orange accent
        'accent_red': HexColor('#ef4444'),       # Red accent
    }
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize enhanced PDF generator"""
        import os
        # Use /tmp directory on Vercel or similar read-only environments
        if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME') or not os.access(output_dir, os.W_OK):
            self.output_dir = Path("/tmp/reports")
        else:
            self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = self._create_modern_styles()
    
    def _create_modern_styles(self) -> Dict[str, ParagraphStyle]:
        """Create modern paragraph styles matching dashboard design"""
        styles = getSampleStyleSheet()
        custom_styles = {}
        
        # Main title (matches hero-title)
        custom_styles['MainTitle'] = ParagraphStyle(
            'MainTitle',
            fontSize=32,
            textColor=self.COLORS['primary_dark'],
            spaceAfter=8,
            alignment=TA_CENTER,
            fontName='Helvetica',
            leading=36
        )
        
        # Subtitle (matches hero-subtitle)
        custom_styles['Subtitle'] = ParagraphStyle(
            'Subtitle',
            fontSize=14,
            textColor=self.COLORS['text_secondary'],
            spaceAfter=24,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        # Section heading (matches section-title)
        custom_styles['SectionHeading'] = ParagraphStyle(
            'SectionHeading',
            fontSize=18,
            textColor=self.COLORS['text_primary'],
            spaceAfter=16,
            spaceBefore=24,
            fontName='Helvetica-Bold',
            leading=22
        )
        
        # Card title (matches insight-title)
        custom_styles['CardTitle'] = ParagraphStyle(
            'CardTitle',
            fontSize=12,
            textColor=self.COLORS['text_primary'],
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        
        # Body text (matches insight-value)
        custom_styles['BodyText'] = ParagraphStyle(
            'BodyText',
            fontSize=11,
            textColor=self.COLORS['text_secondary'],
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=16
        )
        
        # Metric value (for scores and numbers)
        custom_styles['MetricValue'] = ParagraphStyle(
            'MetricValue',
            fontSize=24,
            textColor=self.COLORS['primary_dark'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Component label
        custom_styles['ComponentLabel'] = ParagraphStyle(
            'ComponentLabel',
            fontSize=10,
            textColor=self.COLORS['text_secondary'],
            fontName='Helvetica'
        )
        
        # Branding
        custom_styles['Branding'] = ParagraphStyle(
            'Branding',
            fontSize=10,
            textColor=self.COLORS['text_muted'],
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        # Financial badge
        custom_styles['FinancialBadge'] = ParagraphStyle(
            'FinancialBadge',
            fontSize=10,
            textColor=self.COLORS['accent_blue'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            borderColor=self.COLORS['accent_blue'],
            borderWidth=1,
            borderPadding=4
        )
        
        return custom_styles
    
    def generate_report(
        self,
        company_name: str,
        ai_readiness_data: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """Generate a beautiful PDF report"""
        try:
            # Generate filename
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_company_name}_AI_Readiness_{timestamp}.pdf"
            
            filepath = self.output_dir / filename
            
            # Create the PDF document with custom page template
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=letter,
                rightMargin=48,
                leftMargin=48,
                topMargin=48,
                bottomMargin=48
            )
            
            # Build the content
            story = []
            
            # Cover page
            story.extend(self._create_cover_page(company_name, ai_readiness_data))
            story.append(PageBreak())
            
            # Executive dashboard
            story.extend(self._create_executive_dashboard(ai_readiness_data))
            story.append(PageBreak())
            
            # Score analysis
            story.extend(self._create_score_analysis(ai_readiness_data))
            
            # Key insights
            story.extend(self._create_key_insights(ai_readiness_data))
            story.append(PageBreak())
            
            # Technology signals
            story.extend(self._create_technology_section(ai_readiness_data))
            
            # Hiring analysis
            if ai_readiness_data.get('company_data', {}).get('job_postings'):
                story.extend(self._create_hiring_analysis(ai_readiness_data))
            
            # Financial insights (if applicable)
            if ai_readiness_data.get('is_financial_company'):
                story.append(PageBreak())
                story.extend(self._create_financial_section(ai_readiness_data))
            
            # Strategic recommendations
            story.append(PageBreak())
            story.extend(self._create_recommendations(ai_readiness_data))
            
            # Next steps
            story.extend(self._create_next_steps(ai_readiness_data))
            
            # Build the PDF
            doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
            
            logger.info(f"Enhanced PDF report generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating enhanced PDF report: {e}")
            raise
    
    def _create_cover_page(self, company_name: str, data: Dict[str, Any]) -> List:
        """Create a beautiful cover page with ModelML branding"""
        elements = []
        
        # Add ModelML logo at the top
        try:
            import os
            logo_path = None
            
            # Try multiple possible logo locations
            possible_paths = [
                "/tmp/modelml.png",  # For Vercel
                "static/modelml.png",  # Relative path
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static/modelml.png"),  # Absolute
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    logo_path = path
                    break
            
            if logo_path:
                logo = Image(logo_path, width=80, height=80)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 0.3*inch))
        except Exception as e:
            logger.warning(f"Could not add logo: {e}")
        
        # ModelML branding text
        branding = Paragraph(
            "<b>MODELML</b>",
            ParagraphStyle(
                'CoverBrandingMain',
                fontSize=24,
                textColor=self.COLORS['primary_dark'],
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                letterSpacing=3
            )
        )
        elements.append(branding)
        
        # Subtitle
        subtitle = Paragraph(
            "PROSPECT INTELLIGENCE PLATFORM",
            ParagraphStyle(
                'CoverBrandingSub',
                fontSize=11,
                textColor=self.COLORS['text_secondary'],
                alignment=TA_CENTER,
                fontName='Helvetica',
                letterSpacing=2,
                spaceAfter=36
            )
        )
        elements.append(subtitle)
        
        # Decorative line
        elements.append(HRFlowable(
            width="50%",
            thickness=1,
            color=self.COLORS['border_light'],
            spaceAfter=36,
            spaceBefore=12,
            hAlign='CENTER'
        ))
        elements.append(Spacer(1, 0.5*inch))
        
        # Main title with enhanced styling
        title = Paragraph(
            "AI READINESS ASSESSMENT",
            ParagraphStyle(
                'EnhancedTitle',
                fontSize=32,
                textColor=self.COLORS['primary_dark'],
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                spaceAfter=12
            )
        )
        elements.append(title)
        
        # Company name with better styling
        company = Paragraph(
            f"<font color='#3b82f6'>{company_name}</font>",
            ParagraphStyle(
                'CoverCompany',
                fontSize=28,
                textColor=self.COLORS['accent_blue'],
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                spaceAfter=48
            )
        )
        elements.append(company)
        
        # Score gauge
        score = data.get('ai_readiness_score', 0)
        # Ensure score is a number, not a dict
        if isinstance(score, dict):
            score = score.get('total_score', 0)
        gauge = ScoreGauge(score, width=250, height=250)
        elements.append(gauge)
        elements.append(Spacer(1, 0.3*inch))
        
        # Readiness category
        category = data.get('readiness_category', 'Assessment Pending')
        cat_style = ParagraphStyle(
            'Category',
            fontSize=18,
            textColor=self._get_score_color(score),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph(category, cat_style))
        
        # Date
        elements.append(Spacer(1, 1*inch))
        date_str = datetime.now().strftime("%B %Y")
        date_para = Paragraph(
            date_str,
            ParagraphStyle(
                'CoverDate',
                fontSize=12,
                textColor=self.COLORS['text_secondary'],
                alignment=TA_CENTER
            )
        )
        elements.append(date_para)
        
        # Financial company badge
        if data.get('is_financial_company'):
            elements.append(Spacer(1, 0.2*inch))
            badge = Paragraph(
                "FINANCIAL SERVICES OPTIMIZED",
                self.styles['FinancialBadge']
            )
            elements.append(badge)
        
        return elements
    
    def _create_executive_dashboard(self, data: Dict[str, Any]) -> List:
        """Create executive dashboard matching web design"""
        elements = []
        
        # Title
        elements.append(Paragraph("Executive Dashboard", self.styles['SectionHeading']))
        
        # Key metrics in grid layout
        metrics_data = []
        
        # Score metric
        score = data.get('ai_readiness_score', 0)
        # Ensure score is a number, not a dict
        if isinstance(score, dict):
            score = score.get('total_score', 0)
        score_html = f"""
        <para align="center">
            <font size="24" color="{self._get_score_color(score).hexval()}"><b>{score}</b></font><br/>
            <font size="10" color="#718096">AI Readiness Score</font>
        </para>
        """
        
        # Confidence metric
        confidence = data.get('confidence', 0)
        conf_html = f"""
        <para align="center">
            <font size="24" color="#3b82f6"><b>{confidence:.0%}</b></font><br/>
            <font size="10" color="#718096">Confidence Level</font>
        </para>
        """
        
        # Data sources metric
        sources_count = sum(1 for v in data.get('data_sources', {}).values() if v)
        sources_html = f"""
        <para align="center">
            <font size="24" color="#10b981"><b>{sources_count}</b></font><br/>
            <font size="10" color="#718096">Data Sources</font>
        </para>
        """
        
        metrics_data = [
            [Paragraph(score_html, self.styles['BodyText']),
             Paragraph(conf_html, self.styles['BodyText']),
             Paragraph(sources_html, self.styles['BodyText'])]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#fafbfc')),
            ('BOX', (0, 0), (-1, -1), 1.5, self.COLORS['border_light']),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#f3f4f6')),
            ('PADDING', (0, 0), (-1, -1), 25),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ROUNDEDCORNERS', [10, 10, 10, 10]),
        ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Component scores visualization
        if data.get('component_scores'):
            elements.append(Paragraph("Score Components", self.styles['CardTitle']))
            elements.append(self._create_component_bars(data['component_scores']))
        
        return elements
    
    def _create_component_bars(self, component_scores: Dict[str, float]) -> Table:
        """Create horizontal bar chart for component scores"""
        comp_data = []
        
        # Map component names to readable labels
        label_map = {
            'tech_hiring': 'Technical Hiring',
            'ai_mentions': 'AI Mentions',
            'company_growth': 'Company Growth',
            'industry_adoption': 'Industry Adoption',
            'tech_modernization': 'Tech Modernization',
            'regulatory_compliance': 'Regulatory Compliance',
            'data_governance': 'Data Governance',
            'quantitative_capabilities': 'Quantitative Analysis',
            'aml_kyc_capabilities': 'AML/KYC Systems',
            'ai_ml_maturity': 'AI/ML Maturity'
        }
        
        for comp, score in component_scores.items():
            label = label_map.get(comp, comp.replace('_', ' ').title())
            
            # Create visual bar
            bar_width = (score / 100) * 3  # 3 inches max width
            bar_html = f"""
            <para>
                <font size="10" color="#1a202c">{label}</font><br/>
                <font size="8" color="#718096">{score:.0f}/100</font>
            </para>
            """
            
            # Create bar drawing
            bar_drawing = Drawing(3*inch, 0.4*inch)
            
            # Background bar
            bar_drawing.add(Rect(0, 5, 3*inch, 15, 
                                fillColor=self.COLORS['background_light'],
                                strokeColor=None))
            
            # Score bar
            if score > 0:
                bar_color = self._get_score_color(score)
                bar_drawing.add(Rect(0, 5, bar_width*inch, 15,
                                    fillColor=bar_color,
                                    strokeColor=None))
            
            comp_data.append([
                Paragraph(bar_html, self.styles['ComponentLabel']),
                bar_drawing
            ])
        
        comp_table = Table(comp_data, colWidths=[2.5*inch, 3.5*inch])
        comp_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        return comp_table
    
    def _create_score_analysis(self, data: Dict[str, Any]) -> List:
        """Create detailed score analysis section"""
        elements = []
        
        elements.append(Paragraph("AI Readiness Analysis", self.styles['SectionHeading']))
        
        # Score interpretation
        score = data.get('ai_readiness_score', 0)
        # Ensure score is a number, not a dict
        if isinstance(score, dict):
            score = score.get('total_score', 0)
        interpretation = self._get_score_interpretation(score, data.get('company_name', 'The company'))
        
        elements.append(Paragraph(interpretation, self.styles['BodyText']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Strengths and improvements in two columns
        strengths = data.get('key_strengths', [])
        improvements = data.get('improvement_areas', [])
        
        if strengths or improvements:
            strengths_html = "<b>Key Strengths</b><br/>"
            for s in strengths[:3]:
                strengths_html += f"• {s}<br/>"
            
            improvements_html = "<b>Areas for Improvement</b><br/>"
            for i in improvements[:3]:
                improvements_html += f"• {i}<br/>"
            
            analysis_data = [[
                Paragraph(strengths_html, self.styles['BodyText']),
                Paragraph(improvements_html, self.styles['BodyText'])
            ]]
            
            analysis_table = Table(analysis_data, colWidths=[3*inch, 3*inch])
            analysis_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['background_light']),
                ('PADDING', (0, 0), (-1, -1), 15),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROUNDEDCORNERS', [8, 8, 8, 8]),
            ]))
            
            elements.append(analysis_table)
        
        elements.append(Spacer(1, 0.3*inch))
        return elements
    
    def _create_key_insights(self, data: Dict[str, Any]) -> List:
        """Create key insights cards matching dashboard design"""
        elements = []
        
        elements.append(Paragraph("Key Insights", self.styles['SectionHeading']))
        
        company_data = data.get('company_data', {})
        job_data = company_data.get('job_postings', {})
        news_data = company_data.get('news_insights', {})
        tech_signals = company_data.get('tech_signals', {})
        
        # Create insight cards in 2x2 grid
        insights = []
        
        # Technical Hiring card
        hiring_html = f"""
        <para>
            <font size="11" color="#1a202c"><b>Technical Hiring</b></font><br/>
            <font size="10" color="#718096">{job_data.get('ai_ml_jobs', 0)} AI/ML positions<br/>
            {job_data.get('total_jobs', 0)} total openings</font>
        </para>
        """
        
        # Recent Initiatives card
        trends = news_data.get('recent_trends', [])
        trend_text = trends[0] if trends else "No recent initiatives"
        news_html = f"""
        <para>
            <font size="11" color="#1a202c"><b>Recent Initiatives</b></font><br/>
            <font size="10" color="#718096">{trend_text[:50]}...</font>
        </para>
        """
        
        # Digital Presence card
        web_html = f"""
        <para>
            <font size="11" color="#1a202c"><b>Digital Presence</b></font><br/>
            <font size="10" color="#718096">{tech_signals.get('ai_mentions', 0)} AI mentions<br/>
            {job_data.get('ai_hiring_intensity', 'Unknown')} intensity</font>
        </para>
        """
        
        # Industry Position card
        industry_html = f"""
        <para>
            <font size="11" color="#1a202c"><b>Industry Position</b></font><br/>
            <font size="10" color="#718096">{company_data.get('basic_info', {}).get('industry', 'Unknown')}<br/>
            {data.get('component_scores', {}).get('industry_adoption', 50):.0f}% adoption</font>
        </para>
        """
        
        insights_data = [
            [Paragraph(hiring_html, self.styles['BodyText']),
             Paragraph(news_html, self.styles['BodyText'])],
            [Paragraph(web_html, self.styles['BodyText']),
             Paragraph(industry_html, self.styles['BodyText'])]
        ]
        
        insights_table = Table(insights_data, colWidths=[3*inch, 3*inch])
        insights_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['background_white']),
            ('GRID', (0, 0), (-1, -1), 1, self.COLORS['border_light']),
            ('PADDING', (0, 0), (-1, -1), 15),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))
        
        elements.append(insights_table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_technology_section(self, data: Dict[str, Any]) -> List:
        """Create technology signals section"""
        elements = []
        
        elements.append(Paragraph("Technology Signals", self.styles['SectionHeading']))
        
        tech_signals = data.get('company_data', {}).get('tech_signals', {})
        
        # Tech stack detected
        tech_stack = tech_signals.get('tech_stack', [])
        if tech_stack:
            tech_text = f"<b>Detected Technologies:</b> {', '.join(tech_stack[:8])}"
            elements.append(Paragraph(tech_text, self.styles['BodyText']))
            elements.append(Spacer(1, 0.1*inch))
        
        # AI roles hiring
        ai_roles = tech_signals.get('ai_roles_hiring', [])
        if ai_roles:
            roles_text = f"<b>AI/ML Roles in Demand:</b> {', '.join(ai_roles[:5])}"
            elements.append(Paragraph(roles_text, self.styles['BodyText']))
        
        elements.append(Spacer(1, 0.3*inch))
        return elements
    
    def _create_hiring_analysis(self, data: Dict[str, Any]) -> List:
        """Create hiring analysis section"""
        elements = []
        
        job_data = data.get('company_data', {}).get('job_postings', {})
        
        if job_data.get('total_jobs', 0) > 0:
            elements.append(Paragraph("Talent Acquisition Analysis", self.styles['SectionHeading']))
            
            # Create hiring metrics
            hiring_html = f"""
            <para>
                The organization currently has <b>{job_data.get('total_jobs', 0)} open positions</b>, 
                with <b>{job_data.get('ai_ml_jobs', 0)} AI/ML specific roles</b> and 
                <b>{job_data.get('tech_jobs', 0)} general technology positions</b>. 
                The AI hiring intensity is classified as <b>{job_data.get('ai_hiring_intensity', 'unknown')}</b>.
            </para>
            """
            elements.append(Paragraph(hiring_html, self.styles['BodyText']))
            
            # Top technologies
            top_tech = job_data.get('top_ai_technologies', [])
            if top_tech:
                elements.append(Spacer(1, 0.1*inch))
                elements.append(Paragraph("<b>In-Demand AI/ML Technologies:</b>", self.styles['CardTitle']))
                
                tech_list = []
                for tech in top_tech[:5]:
                    tech_list.append(f"• {tech.get('keyword', 'N/A')} ({tech.get('count', 0)} mentions)")
                
                for item in tech_list:
                    elements.append(Paragraph(item, self.styles['BodyText']))
            
            elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_financial_section(self, data: Dict[str, Any]) -> List:
        """Create financial services specific section"""
        elements = []
        
        elements.append(Paragraph("Financial Services Assessment", self.styles['SectionHeading']))
        
        # Financial badge
        badge_html = """
        <para align="center">
            <font size="10" color="#3b82f6"><b>FINANCIAL SERVICES OPTIMIZED SCORING</b></font>
        </para>
        """
        elements.append(Paragraph(badge_html, self.styles['BodyText']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Financial insights
        financial_insights = data.get('financial_insights', {})
        
        if financial_insights:
            # Regulatory readiness
            reg_score = financial_insights.get('regulatory_readiness', 0)
            reg_html = f"""
            <para>
                <b>Regulatory Compliance Readiness:</b> {reg_score}/100<br/>
                This score reflects the organization's preparedness for AI governance and regulatory requirements 
                specific to financial services.
            </para>
            """
            elements.append(Paragraph(reg_html, self.styles['BodyText']))
            elements.append(Spacer(1, 0.1*inch))
            
            # Risk management
            risk_score = financial_insights.get('risk_management_maturity', 0)
            risk_html = f"""
            <para>
                <b>Risk Management Maturity:</b> {risk_score}/100<br/>
                Assessment of quantitative risk modeling capabilities and AI-driven risk analytics potential.
            </para>
            """
            elements.append(Paragraph(risk_html, self.styles['BodyText']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Sub-sector analysis
        sub_sector = financial_insights.get('sub_sector', 'financial services')
        sector_html = f"""
        <para>
            <b>Financial Sub-Sector:</b> {sub_sector.title()}<br/>
            Industry-specific considerations have been applied to optimize the assessment for {sub_sector} organizations.
        </para>
        """
        elements.append(Paragraph(sector_html, self.styles['BodyText']))
        
        elements.append(Spacer(1, 0.3*inch))
        return elements
    
    def _create_recommendations(self, data: Dict[str, Any]) -> List:
        """Create strategic recommendations section"""
        elements = []
        
        elements.append(Paragraph("Strategic Recommendations", self.styles['SectionHeading']))
        
        recommendations = data.get('recommendations', [])
        
        # Check if recommendations is a list (from scoring engine) or dict (from frontend)
        if isinstance(recommendations, list):
            # Simple list of recommendation strings
            if recommendations:
                for i, rec in enumerate(recommendations[:5], 1):
                    rec_html = f"<b>{i}.</b> {rec}"
                    elements.append(Paragraph(rec_html, self.styles['BodyText']))
                    elements.append(Spacer(1, 0.05*inch))
            else:
                elements.append(Paragraph("No specific recommendations available.", self.styles['BodyText']))
        elif isinstance(recommendations, dict):
            # Structured recommendations from frontend
            # Decision makers
            decision_makers = recommendations.get('decision_makers', [])
            if decision_makers:
                elements.append(Paragraph("<b>Key Decision Makers to Engage:</b>", self.styles['CardTitle']))
                
                for dm in decision_makers[:3]:
                    dm_html = f"""
                    <para>
                        • <b>{dm.get('title', 'Executive')}</b><br/>
                        <font size="10" color="#718096">{dm.get('approach', 'Strategic engagement recommended')}</font>
                    </para>
                    """
                    elements.append(Paragraph(dm_html, self.styles['BodyText']))
                
                elements.append(Spacer(1, 0.2*inch))
            
            # Sales approach
            sales_approach = recommendations.get('sales_approach', {})
            if sales_approach:
                elements.append(Paragraph("<b>Recommended Sales Strategy:</b>", self.styles['CardTitle']))
                
                strategy_html = f"""
                <para>
                    <b>{sales_approach.get('strategy', 'Consultative Approach')}</b><br/>
                    {sales_approach.get('messaging', 'Focus on AI-driven transformation and competitive advantage.')}
                </para>
                """
                elements.append(Paragraph(strategy_html, self.styles['BodyText']))
                elements.append(Spacer(1, 0.2*inch))
            
            # Key talking points
            talking_points = recommendations.get('key_talking_points', [])
            if talking_points:
                elements.append(Paragraph("<b>Key Talking Points:</b>", self.styles['CardTitle']))
                
                for point in talking_points[:4]:
                    elements.append(Paragraph(f"• {point}", self.styles['BodyText']))
        
        elements.append(Spacer(1, 0.3*inch))
        return elements
    
    def _create_next_steps(self, data: Dict[str, Any]) -> List:
        """Create next steps section"""
        elements = []
        
        elements.append(Paragraph("Recommended Next Steps", self.styles['SectionHeading']))
        
        # Handle both list and dict format for recommendations
        recommendations = data.get('recommendations', [])
        if isinstance(recommendations, dict):
            next_steps = recommendations.get('next_steps', [])
        else:
            next_steps = []  # Use default steps if recommendations is a list
        
        if next_steps:
            for i, step in enumerate(next_steps[:5], 1):
                step_html = f"<b>{i}.</b> {step}"
                elements.append(Paragraph(step_html, self.styles['BodyText']))
                elements.append(Spacer(1, 0.05*inch))
        else:
            default_steps = [
                "Schedule an executive briefing to discuss AI opportunities",
                "Conduct a detailed technical assessment",
                "Develop a customized AI roadmap",
                "Identify quick-win AI use cases",
                "Plan pilot project implementation"
            ]
            for i, step in enumerate(default_steps, 1):
                step_html = f"<b>{i}.</b> {step}"
                elements.append(Paragraph(step_html, self.styles['BodyText']))
                elements.append(Spacer(1, 0.05*inch))
        
        # ModelML call to action
        elements.append(Spacer(1, 0.3*inch))
        cta_html = """
        <para align="center">
            <font size="12" color="#0f1419"><b>Ready to accelerate your AI journey?</b></font><br/>
            <font size="10" color="#718096">Contact ModelML for a personalized consultation</font><br/>
            <font size="10" color="#3b82f6"><b>www.modelml.com</b></font>
        </para>
        """
        elements.append(Paragraph(cta_html, self.styles['BodyText']))
        
        return elements
    
    def _add_header_footer(self, canvas, doc):
        """Add elegant header and footer to each page"""
        canvas.saveState()
        
        # Skip header/footer on first page (cover page)
        if canvas.getPageNumber() > 1:
            # Header with ModelML branding
            canvas.setFont('Helvetica-Bold', 10)
            canvas.setFillColor(self.COLORS['primary_dark'])
            canvas.drawString(48, doc.pagesize[1] - 30, "MODELML")
            
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(self.COLORS['text_secondary'])
            canvas.drawString(100, doc.pagesize[1] - 30, "| Prospect Intelligence Platform")
            
            canvas.drawRightString(doc.pagesize[0] - 48, doc.pagesize[1] - 30, 
                                  datetime.now().strftime("%B %d, %Y"))
            
            # Elegant header line with gradient effect
            canvas.setStrokeColor(self.COLORS['accent_blue'])
            canvas.setLineWidth(2)
            canvas.line(48, doc.pagesize[1] - 38, 150, doc.pagesize[1] - 38)
            
            canvas.setStrokeColor(self.COLORS['border_light'])
            canvas.setLineWidth(1)
            canvas.line(150, doc.pagesize[1] - 38, doc.pagesize[0] - 48, doc.pagesize[1] - 38)
        
        # Footer with page numbers
        if canvas.getPageNumber() > 1:
            page_num = canvas.getPageNumber() - 1  # Don't count cover page
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(self.COLORS['text_muted'])
            
            # Footer line
            canvas.setStrokeColor(self.COLORS['border_light'])
            canvas.setLineWidth(0.5)
            canvas.line(48, 40, doc.pagesize[0] - 48, 40)
            
            # Page number
            canvas.drawCentredString(doc.pagesize[0] / 2, 25, f"Page {page_num}")
            
            # Confidential notice
            canvas.setFont('Helvetica-Oblique', 8)
            canvas.setFillColor(self.COLORS['text_muted'])
            canvas.drawString(48, 25, "Confidential - ModelML Proprietary")
        
        canvas.restoreState()
    
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
    
    def _get_score_interpretation(self, score: float, company_name: str) -> str:
        """Get detailed score interpretation"""
        if score >= 80:
            return f"""
            {company_name} demonstrates <b>exceptional AI readiness</b> with a score of {score}/100. 
            The organization shows strong technological capabilities, active AI talent acquisition, 
            and clear strategic initiatives. They are well-positioned to leverage advanced AI solutions 
            and can move quickly to implementation with ModelML's enterprise platform.
            """
        elif score >= 65:
            return f"""
            {company_name} shows <b>strong potential for AI adoption</b> with a score of {score}/100. 
            The organization has solid foundations in place with some AI initiatives already underway. 
            With targeted improvements in key areas, they can maximize AI value creation and achieve 
            competitive advantage through ModelML's solutions.
            """
        elif score >= 50:
            return f"""
            {company_name} displays <b>emerging interest in AI</b> with a score of {score}/100. 
            The organization is beginning to explore AI opportunities but needs to strengthen certain 
            capabilities. A phased approach with ModelML's guidance can help build momentum and ensure 
            successful AI adoption.
            """
        elif score >= 35:
            return f"""
            {company_name} is in the <b>early stages of AI readiness</b> with a score of {score}/100. 
            Foundation building in data infrastructure, talent, and strategy is recommended before 
            major AI initiatives. ModelML can provide strategic consulting to accelerate this journey.
            """
        else:
            return f"""
            {company_name} currently has <b>limited AI readiness</b> with a score of {score}/100. 
            Significant digital transformation efforts should precede AI adoption. ModelML recommends 
            starting with educational workshops and readiness assessments to build a solid foundation.
            """