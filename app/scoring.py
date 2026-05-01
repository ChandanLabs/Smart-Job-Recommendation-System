import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import settings

# Load NLP model
try:
    nlp = spacy.load(settings.SPACY_MODEL)
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", settings.SPACY_MODEL])
    nlp = spacy.load(settings.SPACY_MODEL)

def clean_text(text: str) -> str:
    """Basic text cleaning."""
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
    return " ".join(tokens)

def extract_keywords(text: str) -> set:
    """Extract noun chunks and entities as keywords."""
    doc = nlp(text)
    keywords = set()
    for chunk in doc.noun_chunks:
        # Keep it simple: lowercased root of the chunk
        keywords.add(chunk.root.lemma_.lower())
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "GPE", "LOC", "NORP", "FAC", "EVENT", "WORK_OF_ART", "LAW", "LANGUAGE"]:
            keywords.add(ent.text.lower())
    return keywords

def compute_similarity(text1: str, text2: str) -> float:
    """Compute cosine similarity between two texts using TF-IDF."""
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(sim)
    except ValueError:
        return 0.0

def analyze_resume_jd(resume_text: str, jd_text: str) -> dict:
    """
    Main scoring logic.
    Returns scores and gap analysis.
    """
    clean_resume = clean_text(resume_text)
    clean_jd = clean_text(jd_text)
    
    # Extract keywords
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)
    
    missing_keywords = list(jd_keywords - resume_keywords)
    
    # Calculate Keyword Coverage
    if jd_keywords:
        keyword_coverage = (len(jd_keywords.intersection(resume_keywords)) / len(jd_keywords)) * 100
    else:
        keyword_coverage = 100.0
        
    # Calculate Experience Relevance / Skills Match using Similarity
    # In a real-world scenario, you might parse sections. Here we use the overall similarity as base
    # and adjust slightly based on length or specific heuristics for demonstration.
    base_similarity = compute_similarity(clean_resume, clean_jd) * 100
    
    skills_match = min(base_similarity * 1.1, 100.0) # Boost slightly for skills
    experience_relevance = base_similarity
    
    overall_match_score = (
        (skills_match * settings.WEIGHT_SKILLS) +
        (experience_relevance * settings.WEIGHT_EXPERIENCE) +
        (keyword_coverage * settings.WEIGHT_KEYWORDS)
    )
    
    # Determine actionable suggestions
    if overall_match_score > 80:
        suggested_actions = "Your resume is a strong match. Focus on tailoring your cover letter."
    elif overall_match_score > 50:
        suggested_actions = "Good foundation, but you are missing some key requirements. Add the missing skills to your resume if you have them."
    else:
        suggested_actions = "Significant gaps identified. Consider adding projects or taking courses to build the missing skills before applying."
    
    return {
        "overall_match_score": round(overall_match_score, 2),
        "scores_by_category": {
            "skills_match": round(skills_match, 2),
            "experience_relevance": round(experience_relevance, 2),
            "keyword_coverage": round(keyword_coverage, 2)
        },
        "missing_keywords": missing_keywords[:15], # Limit to top 15
        "missing_skills": missing_keywords[:5],   # For simplicity, returning a subset as skills
        "suggested_actions": suggested_actions
    }
