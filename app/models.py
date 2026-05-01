from pydantic import BaseModel, Field
from typing import List, Dict

class CategoryScores(BaseModel):
    skills_match: float = Field(..., description="Score for skill keyword matching (0-100)")
    experience_relevance: float = Field(..., description="Score for experience relevance (0-100)")
    keyword_coverage: float = Field(..., description="Score for overall keyword coverage (0-100)")

class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., description="The raw text of the candidate's resume")
    jd_text: str = Field(..., description="The raw text of the job description")

class AnalyzeResponse(BaseModel):
    overall_match_score: float = Field(..., description="Weighted overall match score (0-100)")
    scores_by_category: CategoryScores
    missing_keywords: List[str] = Field(..., description="Keywords present in JD but missing in resume")
    missing_skills: List[str] = Field(..., description="Specific skill entities missing in resume")
    suggested_actions: str = Field(..., description="High-level text summary of actionable steps")

class SuggestRequest(BaseModel):
    section_text: str = Field(..., description="The specific resume section (e.g., a job experience bullet) to improve")
    jd_text: str = Field(..., description="The job description to align with")

class SuggestResponse(BaseModel):
    improved_bullets: List[str] = Field(..., description="List of suggested, improved bullet points")
