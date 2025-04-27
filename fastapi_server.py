"""
OSINT Microagent - FastAPI Server
This is the FastAPI server that will run on port 8000.
"""
import logging
import uvicorn
from fastapi import FastAPI, Request, Form, Depends, Query, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional

# Import components
from app.handlers.input_handler import InputHandler
from app.scrapers.search_engines import SearchEngineScraper
from app.scrapers.api_sources import APISources
from app.scrapers.whois_lookup import WhoisLookup
from app.parsers.result_parser import ResultParser
from app.exporters.webhook_exporter import WebhookExporter
from app.exporters.database_logger import DatabaseLogger
from app.config import settings
from app import get_db

# Create the FastAPI application
app = FastAPI(title="Bishdom IntelSleuth", description="OSINT information gathering tool")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Create instances of components
search_engine_scraper = SearchEngineScraper()
api_sources = APISources()
whois_lookup = WhoisLookup()
result_parser = ResultParser()
webhook_exporter = WebhookExporter()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Renders the main page of the application
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/search")
async def search(
    request: Request,
    background_tasks: BackgroundTasks,
    query: str = Form(...),
    webhook_url: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Processes search requests and returns results
    """
    # Validate and identify the input
    is_valid, input_type, parsed_query = InputHandler.validate_and_identify(query)
    
    if not is_valid:
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request, 
                "error": "Invalid input. Please provide a valid email, domain, IP, username, or phone number."
            }
        )
    
    # Determine which sources to use
    sources = InputHandler._get_sources_for_type(input_type)
    
    # Collect results from different sources
    results = {}
    
    # Whois lookup for domains and IPs
    if sources.get("whois", False):
        whois_results = await whois_lookup.perform_lookup(parsed_query, sources)
        results["whois"] = whois_results
    
    # Search engines
    if sources.get("search_engines", False):
        search_query = parsed_query.get("search_query", query)
        search_results = await search_engine_scraper.search_all(search_query, sources)
        results["search_engines"] = search_results
    
    # API sources
    if sources.get("api_sources", False):
        api_results = await api_sources.fetch_all(parsed_query, sources)
        results["api_sources"] = api_results
    
    # Parse and categorize the results
    categorized_results = result_parser.parse_and_categorize(results)
    
    # Generate summary
    summary = result_parser.generate_summary(categorized_results)
    
    # Log query and results to database in background
    database_logger = DatabaseLogger(db) if db else None
    if database_logger:
        background_tasks.add_task(
            database_logger.log_query,
            query=query,
            query_type=input_type.value,
            results=categorized_results
        )
    
    # Send to webhook if URL provided
    if webhook_url:
        background_tasks.add_task(
            webhook_exporter.send_to_webhook,
            results=categorized_results,
            webhook_url=webhook_url
        )
    
    # Return results to user
    return templates.TemplateResponse(
        "results.html", 
        {
            "request": request,
            "query": query,
            "query_type": input_type.value,
            "results": categorized_results,
            "summary": summary
        }
    )

@app.get("/api/search")
async def api_search(
    background_tasks: BackgroundTasks,
    query: str = Query(...),
    webhook_url: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    API endpoint for search requests
    """
    # Validate and identify the input
    is_valid, input_type, parsed_query = InputHandler.validate_and_identify(query)
    
    if not is_valid:
        return {"error": "Invalid input. Please provide a valid email, domain, IP, username, or phone number."}
    
    # Determine which sources to use
    sources = InputHandler._get_sources_for_type(input_type)
    
    # Collect results from different sources
    results = {}
    
    # Whois lookup for domains and IPs
    if sources.get("whois", False):
        whois_results = await whois_lookup.perform_lookup(parsed_query, sources)
        results["whois"] = whois_results
    
    # Search engines
    if sources.get("search_engines", False):
        search_query = parsed_query.get("search_query", query)
        search_results = await search_engine_scraper.search_all(search_query, sources)
        results["search_engines"] = search_results
    
    # API sources
    if sources.get("api_sources", False):
        api_results = await api_sources.fetch_all(parsed_query, sources)
        results["api_sources"] = api_results
    
    # Parse and categorize the results
    categorized_results = result_parser.parse_and_categorize(results)
    
    # Generate summary
    summary = result_parser.generate_summary(categorized_results)
    
    # Log query and results to database in background
    database_logger = DatabaseLogger(db) if db else None
    if database_logger:
        background_tasks.add_task(
            database_logger.log_query,
            query=query,
            query_type=input_type.value,
            results=categorized_results
        )
    
    # Send to webhook if URL provided
    if webhook_url:
        background_tasks.add_task(
            webhook_exporter.send_to_webhook,
            results=categorized_results,
            webhook_url=webhook_url
        )
    
    # Return results as JSON
    return {
        "query": query,
        "query_type": input_type.value,
        "results": categorized_results,
        "summary": summary
    }

@app.get("/api/extract")
async def extract_content(
    url: str = Query(...),
    max_length: int = Query(5000)
):
    """
    API endpoint to extract text content from a URL
    """
    from app.scrapers.web_content_scraper import WebContentScraper
    
    web_scraper = WebContentScraper()
    content = await web_scraper.extract_text_from_url(url)
    
    # Truncate content if it's too long
    if content and "text" in content and len(content["text"]) > max_length:
        content["text"] = content["text"][:max_length] + "..."
    
    return content