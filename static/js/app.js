// Global variable to store analysis results
let currentAnalysisData = null;

function setCompany(companyName) {
    document.getElementById('companyInput').value = companyName;
}

async function analyzeCompany() {
    const companyName = document.getElementById('companyInput').value.trim();
    
    if (!companyName) {
        alert('Please enter a company name');
        return;
    }
    
    // Show progress section
    document.getElementById('progressSection').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('analyzingCompany').textContent = companyName;
    document.getElementById('analyzeBtn').disabled = true;
    
    // Reset progress
    const progressSteps = document.getElementById('progressSteps');
    progressSteps.innerHTML = '';
    
    // Define steps
    const steps = [
        'Fetching company information',
        'Analyzing job postings',
        'Collecting recent news',
        'Analyzing company website',
        'Calculating AI readiness score',
        'Generating sales recommendations'
    ];
    
    // Add step elements
    steps.forEach(step => {
        const stepElement = document.createElement('div');
        stepElement.className = 'progress-step';
        stepElement.innerHTML = `<span>ó</span> ${step}`;
        progressSteps.appendChild(stepElement);
    });
    
    // Simulate progress
    let currentStep = 0;
    const progressInterval = setInterval(() => {
        if (currentStep < steps.length) {
            const stepElements = progressSteps.getElementsByClassName('progress-step');
            if (currentStep > 0) {
                stepElements[currentStep - 1].className = 'progress-step complete';
                stepElements[currentStep - 1].innerHTML = `<span></span> ${steps[currentStep - 1]}`;
            }
            if (currentStep < steps.length) {
                stepElements[currentStep].className = 'progress-step active';
            }
            
            // Update progress bar
            const progress = ((currentStep + 1) / steps.length) * 100;
            document.getElementById('progressFill').style.width = `${progress}%`;
            
            currentStep++;
        }
    }, 800);
    
    try {
        // Make API call
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ company_name: companyName })
        });
        
        const data = await response.json();
        currentAnalysisData = data;
        
        // Stop progress animation
        clearInterval(progressInterval);
        
        // Complete all steps
        const stepElements = progressSteps.getElementsByClassName('progress-step');
        for (let i = 0; i < stepElements.length; i++) {
            stepElements[i].className = 'progress-step complete';
            stepElements[i].innerHTML = `<span></span> ${steps[i]}`;
        }
        document.getElementById('progressFill').style.width = '100%';
        
        // Wait a moment then show results
        setTimeout(() => {
            displayResults(data);
        }, 1000);
        
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while analyzing the company. Please try again.');
        document.getElementById('progressSection').style.display = 'none';
        document.getElementById('analyzeBtn').disabled = false;
        clearInterval(progressInterval);
    }
}

function displayResults(data) {
    // Hide progress, show results
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('analyzeBtn').disabled = false;
    
    // Company Overview
    const companyInfo = data.company_info;
    document.getElementById('companyDetails').innerHTML = `
        <div class="detail-item">
            <span class="detail-label">Company</span>
            <span class="detail-value">${companyInfo.name}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Industry</span>
            <span class="detail-value">${companyInfo.industry}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Employees</span>
            <span class="detail-value">${companyInfo.employeeCount.toLocaleString()}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Location</span>
            <span class="detail-value">${companyInfo.location.city}, ${companyInfo.location.state}</span>
        </div>
    `;
    
    // AI Readiness Score
    const score = data.readiness_score.total_score;
    animateScore(score);
    document.getElementById('readinessLevel').textContent = data.readiness_score.readiness_level;
    
    // Component Scores
    const componentScores = data.readiness_score.component_scores;
    const componentLabels = {
        'tech_hiring': 'Tech Hiring',
        'ai_mentions': 'AI Mentions',
        'company_growth': 'Company Growth',
        'industry_adoption': 'Industry Benchmark',
        'tech_modernization': 'Tech Modernization'
    };
    
    let componentHTML = '';
    for (const [key, value] of Object.entries(componentScores)) {
        componentHTML += `
            <div class="score-component">
                <span class="score-component-label">${componentLabels[key]}</span>
                <span class="score-component-value">${Math.round(value)}/100</span>
            </div>
        `;
    }
    document.getElementById('componentScores').innerHTML = componentHTML;
    
    // Key Insights
    const jobAnalysis = data.job_analysis;
    const newsAnalysis = data.news_analysis;
    const webAnalysis = data.website_analysis;
    
    document.getElementById('hiringInsight').textContent = 
        `${jobAnalysis.ai_ml_positions} AI/ML positions open out of ${jobAnalysis.total_open_positions} total openings`;
    
    document.getElementById('newsInsight').textContent = 
        newsAnalysis.recent_initiatives.length > 0 
        ? newsAnalysis.recent_initiatives[0].title 
        : 'No recent AI initiatives found';
    
    document.getElementById('webInsight').textContent = 
        `${webAnalysis.ai_mentions_count} AI mentions on website, ${webAnalysis.digital_maturity} digital maturity`;
    
    document.getElementById('industryInsight').textContent = 
        `${companyInfo.industry} sector with ${Math.round(componentScores.industry_adoption)}% typical AI adoption`;
    
    // Decision Makers
    const decisionMakers = data.recommendations.decision_makers;
    let dmHTML = '';
    decisionMakers.forEach(dm => {
        dmHTML += `
            <div class="decision-maker">
                <div class="decision-maker-name">${dm.name}</div>
                <div class="decision-maker-title">${dm.title}</div>
                <div class="decision-maker-approach">${dm.approach}</div>
            </div>
        `;
    });
    document.getElementById('decisionMakers').innerHTML = dmHTML;
    
    // Sales Approach
    const approach = data.recommendations.sales_approach;
    const talkingPoints = data.recommendations.key_talking_points;
    const nextSteps = data.recommendations.next_steps;
    
    let approachHTML = `
        <div class="approach-section">
            <h4>Strategy: ${approach.strategy}</h4>
            <p>${approach.messaging}</p>
        </div>
        <div class="approach-section">
            <h4>Key Talking Points</h4>
            <ul>
    `;
    
    talkingPoints.forEach(point => {
        approachHTML += `<li>${point}</li>`;
    });
    
    approachHTML += `
            </ul>
        </div>
        <div class="approach-section">
            <h4>Recommended Next Steps</h4>
            <ul>
    `;
    
    nextSteps.forEach(step => {
        approachHTML += `<li>${step}</li>`;
    });
    
    approachHTML += `
            </ul>
        </div>
    `;
    
    document.getElementById('salesApproach').innerHTML = approachHTML;
}

function animateScore(targetScore) {
    const scoreElement = document.getElementById('scoreNumber');
    const circle = document.getElementById('scoreCircle');
    const circumference = 2 * Math.PI * 90;
    
    let currentScore = 0;
    const increment = targetScore / 50;
    
    const animation = setInterval(() => {
        currentScore += increment;
        if (currentScore >= targetScore) {
            currentScore = targetScore;
            clearInterval(animation);
        }
        
        scoreElement.textContent = Math.round(currentScore);
        
        // Update circle
        const offset = circumference - (currentScore / 100) * circumference;
        circle.style.strokeDashoffset = offset;
        
        // Change color based on score
        if (currentScore >= 80) {
            circle.style.stroke = '#10b981'; // Green
        } else if (currentScore >= 65) {
            circle.style.stroke = '#3b82f6'; // Blue
        } else if (currentScore >= 50) {
            circle.style.stroke = '#f59e0b'; // Orange
        } else {
            circle.style.stroke = '#ef4444'; // Red
        }
    }, 20);
}

function resetAnalysis() {
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('companyInput').value = '';
    currentAnalysisData = null;
}

async function generateReport() {
    if (!currentAnalysisData) {
        alert('No analysis data available');
        return;
    }
    
    try {
        const response = await fetch('/generate_report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentAnalysisData)
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${currentAnalysisData.company_name}_AI_Readiness_Report.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            alert('Error generating report');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while generating the report');
    }
}

// Allow Enter key to trigger analysis
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('companyInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            analyzeCompany();
        }
    });
});