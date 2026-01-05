"""FastAPI application entry point."""

import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .youtube.controller import router as youtube_router
from .core.logging import setup_logging

app = FastAPI(title="Playlist Sorter")

# Setup CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Playlist Sorter"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Register platform-specific routers
app.include_router(youtube_router)

# Future: app.include_router(spotify_router)

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request details."""
    start_time = time.time()
    
    # Extract query parameters
    query_params = dict(request.query_params)
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    
    logger.info(
        f"Path: {request.url.path} | Method: {request.method} | "
        f"Params: {query_params} | Status: {response.status_code} | "
        f"Duration: {process_time:.2f}ms"
    )
    
    return response
