from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

from app.models import AnalyzeRequest, AnalyzeResponse, SuggestRequest, SuggestResponse
from app.scoring import analyze_resume_jd
from app.llm_client import suggest_improvements
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="API for Resume to Job Description matching and intelligence.",
    version="1.0.0"
)

# CORS middleware for potential separate frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup directories for static files and templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")

# Ensure directories exist
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)


@app.get("/", response_class=HTMLResponse, tags=["UI"])
async def read_root(request: Request):
    """Serve the Interactive UI."""
    return templates.TemplateResponse("index.html", {"request": request, "app_name": settings.APP_NAME})


@app.post("/analyze", response_model=AnalyzeResponse, tags=["Intelligence"])
async def analyze_application(request: AnalyzeRequest):
    """
    Analyzes a resume against a job description.
    Returns match scores and gap analysis.
    """
    analysis_results = analyze_resume_jd(request.resume_text, request.jd_text)
    return AnalyzeResponse(**analysis_results)


@app.post("/suggest-bullets", response_model=SuggestResponse, tags=["Intelligence"])
async def generate_suggestions(request: SuggestRequest):
    """
    Generates improved resume bullet points tailored to the job description using LLM.
    """
    improved = suggest_improvements(request.section_text, request.jd_text)
    return SuggestResponse(improved_bullets=improved)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
