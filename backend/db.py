import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./events.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    source_url = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    date_text = Column(String)
    venue = Column(String)
    organizer = Column(String)
    category = Column(String)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    speakers = relationship("Speaker", back_populates="event", cascade="all, delete-orphan")

class Speaker(Base):
    __tablename__ = "speakers"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    name = Column(String, nullable=False)
    title = Column(String)
    company = Column(String)
    bio_snippet = Column(Text)
    linkedin_url = Column(String)      # NEW — only if explicitly on the page
    company_url = Column(String)       # NEW — only if explicitly on the page
    is_founder = Column(String)
    india_signal = Column(String)
    india_signal_reason = Column(Text)
    event = relationship("Event", back_populates="speakers")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_session():
    return SessionLocal()