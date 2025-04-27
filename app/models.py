import sqlalchemy as sa
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class OsintQuery(Base):
    """
    Model for storing OSINT queries
    """
    __tablename__ = "osint_queries"
    
    id = sa.Column(sa.Integer, primary_key=True)
    query_text = sa.Column(sa.String(255), nullable=False)
    query_type = sa.Column(sa.String(50), nullable=False)
    timestamp = sa.Column(sa.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<OsintQuery(id={self.id}, query='{self.query_text}', type='{self.query_type}')>"

class OsintResult(Base):
    """
    Model for storing OSINT query results
    """
    __tablename__ = "osint_results"
    
    id = sa.Column(sa.Integer, primary_key=True)
    query_id = sa.Column(sa.Integer, sa.ForeignKey("osint_queries.id"), nullable=False)
    category = sa.Column(sa.String(50), nullable=False)
    data = sa.Column(sa.Text, nullable=False)  # JSON string
    source = sa.Column(sa.String(50), nullable=False)
    timestamp = sa.Column(sa.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<OsintResult(id={self.id}, query_id={self.query_id}, category='{self.category}')>"

def init_models(base, engine):
    """
    Initialize database models
    
    Args:
        base: SQLAlchemy declarative base
        engine: SQLAlchemy engine
    """
    # Create tables if they don't exist
    base.metadata.create_all(engine)
