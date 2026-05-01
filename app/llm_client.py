import openai
from app.config import settings

def suggest_improvements(section_text: str, jd_text: str) -> list[str]:
    """
    Calls the LLM to suggest improvements for a resume bullet point.
    Model-agnostic design: can be swapped for Azure OpenAI, Anthropic, or Local models.
    """
    if not settings.OPENAI_API_KEY:
        # Fallback for demonstration when API key is missing
        return [
            "Quantify your impact: e.g., 'Improved performance by 20%'.",
            f"Incorporate keywords from the JD like: '{jd_text.split()[:3]}'.",
            "Start the bullet point with a strong action verb (e.g., 'Architected', 'Spearheaded')."
        ]
    
    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        prompt = f"""
        You are an expert career coach and resume writer.
        A candidate wants to improve a specific bullet point from their resume to better align with a Job Description.
        
        Job Description Context:
        {jd_text}
        
        Original Resume Bullet Point:
        {section_text}
        
        Provide 3 specific, improved, and actionable bullet points they could use instead. 
        Focus on impact, metrics, and aligning with the job description's keywords.
        Format your response as a simple newline-separated list of the 3 bullets without numbers or prefixes.
        """
        
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful career coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=250
        )
        
        output = response.choices[0].message.content.strip()
        bullets = [b.strip("-* ") for b in output.split('\n') if b.strip()]
        return bullets[:3] # Ensure max 3
        
    except Exception as e:
        print(f"LLM Error: {e}")
        return ["Error connecting to LLM service. Please check API key and try again."]
