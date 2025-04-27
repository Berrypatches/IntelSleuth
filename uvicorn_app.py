from app import create_app

# Create FastAPI app
app = create_app()

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI application using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)