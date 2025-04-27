import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

Base = declarative_base()

# Database setup
engine = None
SessionLocal = None

if settings.DATABASE_URL:
    try:
        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")

def get_db():
    if not SessionLocal:
        return None
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_app():
    app = FastAPI(title="OSINT Microagent", description="OSINT information gathering tool")
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Templates
    templates = Jinja2Templates(directory="templates")
    
    # Import and register routes
    from app.routes import router
    app.include_router(router)
    
    # Create database tables if not exists
    if engine:
        from app.models import init_models, Base
        init_models(Base, engine)
    
    @app.on_event("startup")
    async def startup():
        logger.info("OSINT Microagent starting up...")
        
        # Make sure database tables are created
        if engine:
            try:
                from app.models import Base
                Base.metadata.create_all(engine)
                logger.info("Database tables created or confirmed")
            except Exception as e:
                logger.error(f"Error creating database tables: {e}")
    
    @app.on_event("shutdown")
    async def shutdown():
        logger.info("OSINT Microagent shutting down...")
    
    return app
