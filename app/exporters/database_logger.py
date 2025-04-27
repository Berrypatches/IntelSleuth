import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from app.models import OsintQuery, OsintResult
from app.config import settings

logger = logging.getLogger(__name__)

class DatabaseLogger:
    """
    Handles logging queries and results to database
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the database logger
        
        Args:
            db_session: SQLAlchemy database session (optional)
        """
        self.db_session = db_session
    
    async def log_query(self, query: str, query_type: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Logs the query and its results to the database
        
        Args:
            query: The query string
            query_type: The type of query (e.g., "email", "domain")
            results: The query results
            
        Returns:
            Dictionary with status and message
        """
        if not self.db_session:
            logger.warning("Database session not available, skipping logging")
            return {
                "success": False,
                "message": "Database connection not available"
            }
        
        try:
            # Create query record
            query_record = OsintQuery(
                query_text=query,
                query_type=query_type,
                timestamp=datetime.now()
            )
            
            self.db_session.add(query_record)
            self.db_session.flush()  # Get the ID without committing
            
            # Create result records for each category
            for category, items in results.items():
                if category in ["summary", "raw_results"]:
                    continue  # Skip non-category fields
                
                if items and isinstance(items, list):
                    for item in items:
                        result_record = OsintResult(
                            query_id=query_record.id,
                            category=category,
                            data=json.dumps(item),
                            source=item.get("source", "unknown")
                        )
                        self.db_session.add(result_record)
            
            # Commit all records
            self.db_session.commit()
            
            logger.info(f"Successfully logged query and results to database: {query}")
            return {
                "success": True,
                "message": "Query and results successfully logged to database",
                "query_id": query_record.id
            }
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error logging to database: {e}")
            return {
                "success": False,
                "message": f"Database error: {str(e)}"
            }
