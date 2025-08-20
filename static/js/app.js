// Global variable to store analysis results
let currentAnalysisData = null;
let autocompleteTimeout = null;
let selectedSuggestionIndex = -1;

function setCompany(companyName) {
    document.getElementById('companyInput').value = companyName;
    hideAutocomplete();
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
    document.getElementById('progressPercentage').textContent = '0%';
    
    // Define steps
    const steps = [
        { icon: '🔍', text: 'Fetching company information' },
        { icon: '💼', text: 'Analyzing job postings' },
        { icon: '📰', text: 'Collecting recent news' },
        { icon: '🌐', text: 'Analyzing company website' },
        { icon: '📊', text: 'Calculating AI readiness score' },
        { icon: '💡', text: 'Generating sales recommendations' }
    ];
    
    // Add step elements
    steps.forEach(step => {
        const stepElement = document.createElement('div');
        stepElement.className = 'progress-step';
        stepElement.innerHTML = `<span>${step.icon}</span> ${step.text}`;
        progressSteps.appendChild(stepElement);
    });
    
    // Simulate progress
    let currentStep = 0;
    const progressInterval = setInterval(() => {
        if (currentStep < steps.length) {
            const stepElements = progressSteps.getElementsByClassName('progress-step');
            if (currentStep > 0) {
                stepElements[currentStep - 1].className = 'progress-step complete';
                stepElements[currentStep - 1].innerHTML = `<span>✅</span> ${steps[currentStep - 1].text}`;
            }
            if (currentStep < steps.length) {
                stepElements[currentStep].className = 'progress-step active';
            }
            
            // Update progress bar and percentage
            const progress = ((currentStep + 1) / steps.length) * 100;
            document.getElementById('progressFill').style.width = `${progress}%`;
            document.getElementById('progressPercentage').textContent = `${Math.round(progress)}%`;
            
            currentStep++;
        }
    }, 800);
    
    try {
        // Make API call
        const response = await fetch('/analyze/comprehensive', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: companyName })
        });
        
        const data = await response.json();
        currentAnalysisData = data;
        
        // Stop progress animation
        clearInterval(progressInterval);
        
        // Complete all steps
        const stepElements = progressSteps.getElementsByClassName('progress-step');
        for (let i = 0; i < stepElements.length; i++) {
            stepElements[i].className = 'progress-step complete';
            stepElements[i].innerHTML = `<span>✅</span> ${steps[i].text}`;
        }
        document.getElementById('progressFill').style.width = '100%';
        document.getElementById('progressPercentage').textContent = '100%';
        
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
    
    // Company name and date
    document.getElementById('resultCompanyName').textContent = data.company_name;
    document.getElementById('analysisDate').textContent = new Date().toLocaleDateString('en-US', { 
        month: 'long', 
        day: 'numeric', 
        year: 'numeric' 
    });
    
    // AI Readiness Score
    const score = data.ai_readiness_score;
    animateScore(score);
    document.getElementById('readinessLevel').textContent = data.readiness_category;
    
    // Set readiness badge color based on score
    const badge = document.getElementById('readinessBadge');
    if (score >= 80) {
        badge.style.background = 'rgba(16, 185, 129, 0.1)';
        badge.style.color = '#10b981';
    } else if (score >= 65) {
        badge.style.background = 'rgba(59, 130, 246, 0.1)';
        badge.style.color = '#3b82f6';
    } else if (score >= 50) {
        badge.style.background = 'rgba(245, 158, 11, 0.1)';
        badge.style.color = '#f59e0b';
    } else {
        badge.style.background = 'rgba(239, 68, 68, 0.1)';
        badge.style.color = '#ef4444';
    }
    
    // Component Scores
    const componentScores = data.component_scores || {};
    const componentLabels = {
        'tech_hiring': 'Technical Hiring',
        'ai_mentions': 'AI Mentions',
        'company_growth': 'Company Growth',
        'industry_adoption': 'Industry Benchmark',
        'tech_modernization': 'Tech Modernization',
        'regulatory_compliance': 'Regulatory Compliance',
        'data_governance': 'Data Governance',
        'quantitative_capabilities': 'Quantitative Capabilities',
        'aml_kyc_capabilities': 'AML/KYC Capabilities',
        'ai_ml_maturity': 'AI/ML Maturity'
    };
    
    let componentHTML = '';
    for (const [key, value] of Object.entries(componentScores)) {
        const percentage = Math.round(value);
        let barColor = '#10b981';
        if (percentage < 50) barColor = '#ef4444';
        else if (percentage < 70) barColor = '#f59e0b';
        
        componentHTML += `
            <div class="score-component">
                <span class="score-component-label">${componentLabels[key]}</span>
                <span class="score-component-value">${percentage}/100</span>
            </div>
        `;
    }
    document.getElementById('componentScores').innerHTML = componentHTML;
    
    // Key Insights
    const companyData = data.company_data || {};
    const jobData = companyData.job_postings || {};
    const newsData = companyData.news_insights || {};
    const techSignals = companyData.tech_signals || {};
    const basicInfo = companyData.basic_info || {};
    
    document.getElementById('hiringInsight').textContent = 
        `${jobData.ai_ml_jobs || 0} AI/ML positions open out of ${jobData.total_jobs || 0} total openings`;
    
    document.getElementById('newsInsight').textContent = 
        newsData.recent_trends && newsData.recent_trends.length > 0 
        ? newsData.recent_trends[0] 
        : 'No recent AI initiatives found';
    
    document.getElementById('webInsight').textContent = 
        `${techSignals.ai_mentions || 0} AI mentions on website, ${jobData.ai_hiring_intensity || 'unknown'} AI hiring intensity`;
    
    document.getElementById('industryInsight').textContent = 
        `${basicInfo.industry || 'Unknown'} sector with ${Math.round(componentScores.industry_adoption || 50)}% typical AI adoption`;
    
    // Decision Makers
    const recommendations = data.recommendations || {};
    const decisionMakers = recommendations.decision_makers || [];
    let dmHTML = '';
    if (decisionMakers.length > 0) {
        decisionMakers.forEach(dm => {
            dmHTML += `
                <div class="decision-maker">
                    <div class="decision-maker-name">${dm.name}</div>
                    <div class="decision-maker-title">${dm.title}</div>
                    <div class="decision-maker-approach">${dm.approach}</div>
                </div>
            `;
        });
    } else {
        dmHTML = '<p class="insight-value">Key decision makers analysis available in full report</p>';
    }
    document.getElementById('decisionMakers').innerHTML = dmHTML;
    
    // Sales Approach
    const approach = recommendations.sales_approach || { strategy: 'Standard', messaging: 'Contact for detailed analysis' };
    const talkingPoints = recommendations.key_talking_points || ['Leverage AI for competitive advantage', 'Automate repetitive tasks', 'Enhance decision-making with data'];
    const nextSteps = recommendations.next_steps || ['Schedule discovery call', 'Prepare customized demo', 'Share case studies'];
    
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
    const circumference = 2 * Math.PI * 85; // Updated radius to 85
    
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
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function generateReport() {
    if (!currentAnalysisData) {
        alert('No analysis data available');
        return;
    }
    
    // Add loading state to button
    const button = event.target.closest('.action-button');
    const originalContent = button.innerHTML;
    button.innerHTML = '<span>Generating...</span>';
    button.disabled = true;
    
    try {
        const response = await fetch('/generate-report', {
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
            a.download = `${currentAnalysisData.company_name || 'Company'}_AI_Readiness_Report.pdf`;
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
    } finally {
        // Restore button state
        button.innerHTML = originalContent;
        button.disabled = false;
    }
}

// Autocomplete functions
async function fetchCompanySuggestions(query) {
    if (query.length < 2) {
        return [];
    }
    
    try {
        const response = await fetch(`/api/company-suggestions?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        return data.suggestions || [];
    } catch (error) {
        console.error('Error fetching suggestions:', error);
        return [];
    }
}

function showAutocomplete(suggestions) {
    const dropdown = document.getElementById('autocompleteDropdown');
    if (!dropdown) return;
    
    if (suggestions.length === 0) {
        hideAutocomplete();
        return;
    }
    
    let html = '';
    suggestions.forEach((company, index) => {
        const ticker = company.ticker ? ` (${company.ticker})` : '';
        html += `
            <div class="autocomplete-item ${index === selectedSuggestionIndex ? 'selected' : ''}" 
                 data-index="${index}"
                 data-name="${company.name}">
                <div class="autocomplete-company">
                    <span class="autocomplete-name">${company.name}${ticker}</span>
                    <span class="autocomplete-type">${company.type}</span>
                </div>
            </div>
        `;
    });
    
    dropdown.innerHTML = html;
    dropdown.style.display = 'block';
    
    // Add click handlers to suggestions
    dropdown.querySelectorAll('.autocomplete-item').forEach(item => {
        item.addEventListener('click', function() {
            const companyName = this.getAttribute('data-name');
            setCompany(companyName);
        });
    });
}

function hideAutocomplete() {
    const dropdown = document.getElementById('autocompleteDropdown');
    if (dropdown) {
        dropdown.style.display = 'none';
        dropdown.innerHTML = '';
    }
    selectedSuggestionIndex = -1;
}

function handleAutocompleteKeyboard(e) {
    const dropdown = document.getElementById('autocompleteDropdown');
    if (!dropdown || dropdown.style.display === 'none') return false;
    
    const items = dropdown.querySelectorAll('.autocomplete-item');
    if (items.length === 0) return false;
    
    switch(e.key) {
        case 'ArrowDown':
            e.preventDefault();
            selectedSuggestionIndex = Math.min(selectedSuggestionIndex + 1, items.length - 1);
            updateSelectedSuggestion(items);
            return true;
            
        case 'ArrowUp':
            e.preventDefault();
            selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, -1);
            updateSelectedSuggestion(items);
            return true;
            
        case 'Enter':
            if (selectedSuggestionIndex >= 0 && selectedSuggestionIndex < items.length) {
                e.preventDefault();
                const selectedItem = items[selectedSuggestionIndex];
                const companyName = selectedItem.getAttribute('data-name');
                setCompany(companyName);
                return true;
            }
            break;
            
        case 'Escape':
            e.preventDefault();
            hideAutocomplete();
            return true;
    }
    
    return false;
}

function updateSelectedSuggestion(items) {
    items.forEach((item, index) => {
        if (index === selectedSuggestionIndex) {
            item.classList.add('selected');
        } else {
            item.classList.remove('selected');
        }
    });
}

// Allow Enter key to trigger analysis
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('companyInput');
    if (input) {
        // Add autocomplete functionality
        input.addEventListener('input', function() {
            const query = this.value.trim();
            
            // Clear previous timeout
            if (autocompleteTimeout) {
                clearTimeout(autocompleteTimeout);
            }
            
            // Reset selection when typing
            selectedSuggestionIndex = -1;
            
            // Debounce the autocomplete
            autocompleteTimeout = setTimeout(async () => {
                if (query.length >= 2) {
                    const suggestions = await fetchCompanySuggestions(query);
                    showAutocomplete(suggestions);
                } else {
                    hideAutocomplete();
                }
            }, 300);
        });
        
        // Handle keyboard navigation
        input.addEventListener('keydown', function(e) {
            if (handleAutocompleteKeyboard(e)) {
                return; // Event was handled by autocomplete
            }
            
            // Original Enter key handler for analysis
            if (e.key === 'Enter') {
                const dropdown = document.getElementById('autocompleteDropdown');
                if (!dropdown || dropdown.style.display === 'none' || selectedSuggestionIndex === -1) {
                    analyzeCompany();
                }
            }
        });
        
        // Hide autocomplete when clicking outside
        document.addEventListener('click', function(e) {
            const input = document.getElementById('companyInput');
            const dropdown = document.getElementById('autocompleteDropdown');
            
            if (!input.contains(e.target) && !dropdown.contains(e.target)) {
                hideAutocomplete();
            }
        });
    }
    
    // Add smooth scroll behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});