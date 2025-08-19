"""
SQLAlchemy models for Prospect Intelligence Tool
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
try:
    from database import Base
except ImportError:
    from .database import Base


class CompanySizeCategory(enum.Enum):
    """Enum for company size categories"""
    STARTUP = "startup"
    SMB = "smb"
    ENTERPRISE = "enterprise"


class SignalType(enum.Enum):
    """Enum for technology signal types"""
    JOB_POSTING = "job_posting"
    NEWS_MENTION = "news_mention"
    PRESS_RELEASE = "press_release"
    WEBSITE_CONTENT = "website_content"
    SOCIAL_MEDIA = "social_media"


class Company(Base):
    """
    Company model representing a prospect company
    """
    __tablename__ = "companies"

    # Primary key using UUID
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Company basic information
    name = Column(String(255), nullable=False, index=True)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    industry = Column(String(255), nullable=True)
    size_category = Column(Enum(CompanySizeCategory), nullable=True)
    headquarters = Column(String(255), nullable=True)
    
    # Additional company data
    employee_count = Column(Integer, nullable=True)
    revenue_range = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tech_signals = relationship("TechSignal", back_populates="company", cascade="all, delete-orphan")
    ai_readiness_scores = relationship("AIReadinessScore", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name}, domain={self.domain})>"


class TechSignal(Base):
    """
    Technology signals collected from various sources about a company
    """
    __tablename__ = "tech_signals"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to Company
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    
    # Signal information
    signal_type = Column(Enum(SignalType), nullable=False, index=True)
    content = Column(Text, nullable=False)
    source = Column(String(255), nullable=False)
    source_url = Column(String(500), nullable=True)
    
    # Signal metadata
    date = Column(DateTime(timezone=True), nullable=False)
    relevance_score = Column(Integer, nullable=False, default=50)  # 0-100
    
    # AI/Tech specific indicators
    ai_mentioned = Column(Integer, default=0)  # Count of AI mentions
    tech_keywords = Column(JSON, nullable=True)  # List of identified tech keywords
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="tech_signals")
    
    def __repr__(self):
        return f"<TechSignal(id={self.id}, type={self.signal_type.value}, company_id={self.company_id})>"


class AIReadinessScore(Base):
    """
    AI readiness scores and assessment for companies
    """
    __tablename__ = "ai_readiness_scores"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to Company
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    
    # Overall score and components
    overall_score = Column(Integer, nullable=False)  # 0-100
    confidence = Column(Float, nullable=False, default=0.5)  # 0.0-1.0
    
    # Component scores stored as JSON
    # Expected structure: {
    #   "tech_hires": 85,
    #   "ai_mentions": 70,
    #   "company_size": 60,
    #   "industry_adoption": 75,
    #   "modernization_signals": 80
    # }
    component_scores = Column(JSON, nullable=False)
    
    # Analysis details
    analysis_summary = Column(Text, nullable=True)
    recommendations = Column(JSON, nullable=True)  # List of recommended actions
    decision_makers = Column(JSON, nullable=True)  # List of identified decision makers
    
    # Metadata
    data_sources_used = Column(JSON, nullable=True)  # List of data sources
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="ai_readiness_scores")
    
    def __repr__(self):
        return f"<AIReadinessScore(id={self.id}, company_id={self.company_id}, score={self.overall_score})>"
    
    @property
    def is_high_potential(self):
        """Check if company is high potential prospect (score >= 70)"""
        return self.overall_score >= 70
    
    @property
    def readiness_category(self):
        """Categorize readiness level"""
        if self.overall_score >= 80:
            return "Very Ready"
        elif self.overall_score >= 60:
            return "Ready"
        elif self.overall_score >= 40:
            return "Somewhat Ready"
        else:
            return "Not Ready"