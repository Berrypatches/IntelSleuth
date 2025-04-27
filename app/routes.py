import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Form, Depends, BackgroundTasks, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import json

from app.handlers.input_handler import InputHandler
from app.scrapers.search_engines import SearchEngineScraper
from app.scrapers.api_sources import APISources
from app.scrapers.whois_lookup import WhoisLookup
from app.scrapers.web_content_scraper import WebContentScraper
from app.parsers.result_parser import ResultParser
from app.exporters.webhook_exporter import WebhookExporter
from app.exporters.database_logger import DatabaseLogger
from app.utils import sanitize_input
from app import get_db

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Renders the main page of the application
    """
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/search")
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
    # Sanitize inputs
    query = sanitize_input(query)
    if not query:
        return templates.TemplateResponse(
            "index.html", 
            {"request": request, "error": "Please provide a valid search query"}
        )
    
    # Parse and validate query
    input_handler = InputHandler()
    parsed_query = input_handler.parse_query(query)
    
    if not parsed_query["valid"]:
        return templates.TemplateResponse(
            "index.html", 
            {"request": request, "error": "Invalid query format"}
        )
    
    # Initialize components
    search_scraper = SearchEngineScraper()
    api_sources = APISources()
    whois_lookup = WhoisLookup()
    web_scraper = WebContentScraper()
    result_parser = ResultParser()
    webhook_exporter = WebhookExporter()
    db_logger = DatabaseLogger(db_session=db) if db else None
    
    # Gather data from all sources
    search_results = await search_scraper.search_all(
        query, parsed_query["sources"]
    )
    
    api_results = await api_sources.fetch_all(
        parsed_query["data"], parsed_query["sources"]
    )
    
    whois_results = await whois_lookup.perform_lookup(
        parsed_query["data"], parsed_query["sources"]
    )
    
    # Get content from top search result URLs if domain search
    web_content_results = {}
    if parsed_query["type"] == "domain" and search_results.get("duckduckgo"):
        # Extract first 3 URLs from search results
        urls = [result["url"] for result in search_results.get("duckduckgo", [])[:3]]
        if urls:
            web_content_results = await web_scraper.process_urls(urls, max_urls=3)
    
    # Combine all results
    all_results = {
        "search_results": search_results,
        "api_results": api_results,
        "whois_results": whois_results,
        "web_content_results": web_content_results
    }
    
    # Parse and categorize results
    categorized_results = result_parser.parse_and_categorize(all_results)
    
    # Generate summary
    summary = result_parser.generate_summary(categorized_results)
    
    # Add summary to results
    categorized_results["summary"] = summary
    
    # Schedule background tasks
    if webhook_url:
        # Format results for n8n if webhook provided
        n8n_payload = await webhook_exporter.format_for_n8n(categorized_results, query)
        background_tasks.add_task(webhook_exporter.send_to_webhook, n8n_payload, webhook_url)
    
    if db_logger:
        background_tasks.add_task(
            db_logger.log_query, 
            query, 
            str(parsed_query["type"]), 
            categorized_results
        )
    
    # Render results page
    return templates.TemplateResponse(
        "results.html", 
        {
            "request": request, 
            "query": query,
            "query_type": parsed_query["type"],
            "results": categorized_results,
            "summary": summary
        }
    )

@router.get("/api/search", response_class=JSONResponse)
async def api_search(
    background_tasks: BackgroundTasks,
    query: str = Query(...),
    webhook_url: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    API endpoint for search requests
    """
    # Sanitize inputs
    query = sanitize_input(query)
    if not query:
        raise HTTPException(status_code=400, detail="Please provide a valid search query")
    
    # Parse and validate query
    input_handler = InputHandler()
    parsed_query = input_handler.parse_query(query)
    
    if not parsed_query["valid"]:
        raise HTTPException(status_code=400, detail="Invalid query format")
    
    # Initialize components
    search_scraper = SearchEngineScraper()
    api_sources = APISources()
    whois_lookup = WhoisLookup()
    web_scraper = WebContentScraper()
    result_parser = ResultParser()
    webhook_exporter = WebhookExporter()
    db_logger = DatabaseLogger(db_session=db) if db else None
    
    # Gather data from all sources
    search_results = await search_scraper.search_all(
        query, parsed_query["sources"]
    )
    
    api_results = await api_sources.fetch_all(
        parsed_query["data"], parsed_query["sources"]
    )
    
    whois_results = await whois_lookup.perform_lookup(
        parsed_query["data"], parsed_query["sources"]
    )
    
    # Get content from top search result URLs if domain search
    web_content_results = {}
    if parsed_query["type"] == "domain" and search_results.get("duckduckgo"):
        # Extract first 3 URLs from search results
        urls = [result["url"] for result in search_results.get("duckduckgo", [])[:3]]
        if urls:
            web_content_results = await web_scraper.process_urls(urls, max_urls=3)
    
    # Combine all results
    all_results = {
        "search_results": search_results,
        "api_results": api_results,
        "whois_results": whois_results,
        "web_content_results": web_content_results
    }
    
    # Parse and categorize results
    categorized_results = result_parser.parse_and_categorize(all_results)
    
    # Generate summary
    summary = result_parser.generate_summary(categorized_results)
    
    # Add summary to results
    categorized_results["summary"] = summary
    
    # Schedule background tasks
    if webhook_url:
        # Format results for n8n if webhook provided
        n8n_payload = await webhook_exporter.format_for_n8n(categorized_results, query)
        background_tasks.add_task(webhook_exporter.send_to_webhook, n8n_payload, webhook_url)
    
    if db_logger:
        background_tasks.add_task(
            db_logger.log_query, 
            query, 
            str(parsed_query["type"]), 
            categorized_results
        )
    
    # Return JSON response
    return {
        "query": query,
        "query_type": parsed_query["type"],
        "results": categorized_results
    }

@router.get("/api/extract-content", response_class=JSONResponse)
async def extract_content(
    url: str = Query(...),
    max_length: int = Query(5000)
):
    """
    API endpoint to extract text content from a URL
    """
    if not url:
        raise HTTPException(status_code=400, detail="Please provide a valid URL")
    
    web_scraper = WebContentScraper()
    result = await web_scraper.extract_text_from_url(url)
    
    # Trim content if needed
    if result.get("content") and len(result["content"]) > max_length:
        result["content"] = result["content"][:max_length] + "..."
        result["truncated"] = True
    
    return result