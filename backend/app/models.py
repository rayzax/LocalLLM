"""
SQLAlchemy database models.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Conversation(Base):
    """Conversation model for storing chat sessions."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="New Conversation")
    model = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    tags = Column(JSON, default=list)  # List of tags for categorization
    system_prompt = Column(Text, nullable=True)
    is_archived = Column(Boolean, default=False)

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Message model for storing individual chat messages."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    token_count = Column(Integer, default=0)
    extra_metadata = Column(JSON, default=dict)  # For storing additional data (citations, etc.)

    # Model parameters (for assistant messages)
    temperature = Column(Float, nullable=True)
    top_p = Column(Float, nullable=True)
    max_tokens = Column(Integer, nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class IndexedFile(Base):
    """Model for tracking indexed files in RAG system."""

    __tablename__ = "indexed_files"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(1024), nullable=False, unique=True, index=True)
    file_hash = Column(String(64), nullable=False)  # SHA256 hash
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    last_modified = Column(DateTime, nullable=False)
    indexed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    chunk_count = Column(Integer, default=0)
    status = Column(String(20), default="indexed")  # 'pending', 'indexed', 'failed', 'deleted'
    error_message = Column(Text, nullable=True)


class AppSettings(Base):
    """Application settings stored in database."""

    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ResearchSession(Base):
    """Model for storing research sessions."""

    __tablename__ = "research_sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    query = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="in_progress")  # 'in_progress', 'completed', 'failed'
    sources = Column(JSON, default=list)  # List of source URLs and metadata
    findings = Column(Text, nullable=True)
    report = Column(Text, nullable=True)


class PromptTemplate(Base):
    """Model for storing reusable prompt templates."""

    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    template = Column(Text, nullable=False)
    variables = Column(JSON, default=list)  # List of variable names
    category = Column(String(100), nullable=True)
    is_system_prompt = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    use_count = Column(Integer, default=0)
