document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const suggestBtn = document.getElementById('suggestBtn');
    const resumeText = document.getElementById('resumeText');
    const jdText = document.getElementById('jdText');
    
    // UI Elements
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsSection = document.getElementById('resultsSection');
    
    analyzeBtn.addEventListener('click', async () => {
        const resume = resumeText.value.trim();
        const jd = jdText.value.trim();
        
        if (!resume || !jd) {
            alert('Please paste both your resume and the job description.');
            return;
        }
        
        // Show loading
        resultsSection.classList.add('hidden');
        loadingIndicator.classList.remove('hidden');
        analyzeBtn.disabled = true;
        
        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ resume_text: resume, jd_text: jd })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                displayResults(data);
            } else {
                alert('Error analyzing data: ' + (data.detail || 'Unknown error'));
            }
        } catch (error) {
            console.error('API Error:', error);
            alert('Failed to connect to the server.');
        } finally {
            loadingIndicator.classList.add('hidden');
            analyzeBtn.disabled = false;
        }
    });
    
    suggestBtn.addEventListener('click', async () => {
        const bulletInput = document.getElementById('bulletInput').value.trim();
        const jd = jdText.value.trim();
        
        if (!bulletInput) {
            alert('Please enter a bullet point to improve.');
            return;
        }
        if (!jd) {
            alert('Please ensure the job description is filled out.');
            return;
        }
        
        const bulletLoading = document.getElementById('bulletLoading');
        const bulletSuggestions = document.getElementById('bulletSuggestions');
        
        bulletSuggestions.classList.add('hidden');
        bulletLoading.classList.remove('hidden');
        suggestBtn.disabled = true;
        
        try {
            const response = await fetch('/suggest-bullets', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ section_text: bulletInput, jd_text: jd })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                bulletSuggestions.innerHTML = '';
                data.improved_bullets.forEach(bullet => {
                    const div = document.createElement('div');
                    div.className = 'suggestion-item';
                    div.textContent = bullet;
                    bulletSuggestions.appendChild(div);
                });
                bulletSuggestions.classList.remove('hidden');
            } else {
                alert('Error generating suggestions.');
            }
        } catch (error) {
            console.error('API Error:', error);
        } finally {
            bulletLoading.classList.add('hidden');
            suggestBtn.disabled = false;
        }
    });
});

function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.classList.remove('hidden');
    
    // Animate Overall Score Circle
    const overallScore = data.overall_match_score;
    const circle = document.getElementById('overallScoreCircle');
    const text = document.getElementById('overallScoreText');
    
    setTimeout(() => {
        circle.setAttribute('stroke-dasharray', `${overallScore}, 100`);
        circle.style.stroke = getColorForScore(overallScore);
        animateNumber(text, overallScore);
    }, 100);
    
    // Animate Category Bars
    updateBar('skillsBar', 'skillsScore', data.scores_by_category.skills_match);
    updateBar('expBar', 'expScore', data.scores_by_category.experience_relevance);
    updateBar('keywordBar', 'keywordScore', data.scores_by_category.keyword_coverage);
    
    // Actions and Keywords
    document.getElementById('actionableSuggestions').textContent = data.suggested_actions;
    
    const keywordsContainer = document.getElementById('missingKeywords');
    keywordsContainer.innerHTML = '';
    
    if (data.missing_keywords.length === 0) {
        keywordsContainer.innerHTML = '<span class="chip">None! You matched perfectly.</span>';
    } else {
        data.missing_keywords.forEach(kw => {
            const span = document.createElement('span');
            span.className = 'chip';
            span.textContent = kw;
            keywordsContainer.appendChild(span);
        });
    }
}

function updateBar(barId, textId, value) {
    const bar = document.getElementById(barId);
    const text = document.getElementById(textId);
    
    setTimeout(() => {
        bar.style.width = `${value}%`;
        bar.style.background = getColorForScore(value);
        animateNumber(text, value, true);
    }, 100);
}

function getColorForScore(score) {
    if (score >= 75) return 'var(--success)';
    if (score >= 50) return 'var(--warning)';
    return 'var(--danger)';
}

function animateNumber(element, target, appendPercent = false) {
    let current = 0;
    const inc = target / 30; // 30 frames
    const timer = setInterval(() => {
        current += inc;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.round(current) + '%';
    }, 30);
}
