// ModelML Prospect Intelligence Tool - Frontend JavaScript

let currentAnalysisData = null;
let websocket = null;

// DOM Elements
const form = document.getElementById('analysisForm');
const companyNameInput = document.getElementById('companyName');
const companyDomainInput = document.getElementById('companyDomain');
const analyzeBtn = document.getElementById('analyzeBtn');
const resetBtn = document.getElementById('resetBtn');
const progressSection = document.getElementById('progressSection');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const resultsSection = document.getElementById('resultsSection');
const errorMessage = document.getElementById('errorMessage');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');
const downloadPdfBtn = document.getElementById('downloadPdfBtn');

// Score display elements
const scoreValue = document.getElementById('scoreValue');
const scoreCategory = document.getElementById('scoreCategory');
const confidenceValue = document.getElementById('confidenceValue');
const techHiringValue = document.getElementById('techHiringValue');
const aiMentionsValue = document.getElementById('aiMentionsValue');
const industryValue = document.getElementById('industryValue');

// Event Listeners
form.addEventListener('submit', handleFormSubmit);
resetBtn.addEventListener('click', resetForm);
newAnalysisBtn.addEventListener('click', startNewAnalysis);
downloadPdfBtn.addEventListener('click', downloadPdfReport);

// WebSocket setup for real-time updates
function setupWebSocket() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws`;
    
    try {
        websocket = new WebSocket(wsUrl);
        
        websocket.onopen = () => {
            console.log('WebSocket connected');
        };
        
        websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            updateProgress(data.progress, data.message);
        };
        
        websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        websocket.onclose = () => {
            console.log('WebSocket disconnected');
        };
    } catch (error) {
        console.log('WebSocket not available, using polling instead');
    }
}

// Handle form submission
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const companyName = companyNameInput.value.trim();
    const companyDomain = companyDomainInput.value.trim();
    
    if (!companyName) {
        showError('Please enter a company name');
        return;
    }
    
    // Prepare request data
    const requestData = {
        name: companyName
    };
    
    if (companyDomain) {
        requestData.domain = companyDomain;
    }
    
    // Start analysis
    startAnalysis();
    
    try {
        // First, run comprehensive analysis
        const analysisResponse = await fetch('/analyze/comprehensive', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!analysisResponse.ok) {
            throw new Error(`Analysis failed: ${analysisResponse.statusText}`);
        }
        
        currentAnalysisData = await analysisResponse.json();
        
        // Update progress
        updateProgress(100, 'Analysis complete!');
        
        // Display results
        setTimeout(() => {
            displayResults(currentAnalysisData);
        }, 500);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(`Analysis failed: ${error.message}`);
        hideProgress();
    }
}

// Start analysis UI state
function startAnalysis() {
    // Hide any previous errors
    hideError();
    
    // Hide results if shown
    resultsSection.style.display = 'none';
    
    // Show progress section
    progressSection.style.display = 'block';
    
    // Disable form
    analyzeBtn.disabled = true;
    companyNameInput.disabled = true;
    companyDomainInput.disabled = true;
    
    // Initialize progress
    updateProgress(0, 'Initializing analysis...');
    
    // Simulate progress updates if WebSocket not available
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
        simulateProgress();
    }
}

// Simulate progress updates
function simulateProgress() {
    const progressSteps = [
        { progress: 20, message: 'Fetching company data...', delay: 500 },
        { progress: 40, message: 'Analyzing web presence...', delay: 1500 },
        { progress: 60, message: 'Collecting job postings...', delay: 2500 },
        { progress: 80, message: 'Calculating AI readiness score...', delay: 3500 }
    ];
    
    progressSteps.forEach(step => {
        setTimeout(() => {
            if (progressSection.style.display === 'block') {
                updateProgress(step.progress, step.message);
            }
        }, step.delay);
    });
}

// Update progress bar and text
function updateProgress(progress, message) {
    progressBar.style.width = `${progress}%`;
    progressText.textContent = message;
}

// Display analysis results
function displayResults(data) {
    // Hide progress
    hideProgress();
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Update score display
    scoreValue.textContent = data.ai_readiness_score || '--';
    scoreCategory.textContent = data.readiness_category || 'AI Readiness Score';
    
    // Set score color based on value
    const score = data.ai_readiness_score || 0;
    if (score >= 67) {
        scoreValue.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
    } else if (score >= 34) {
        scoreValue.style.background = 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)';
    } else {
        scoreValue.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
    }
    scoreValue.style.webkitBackgroundClip = 'text';
    scoreValue.style.webkitTextFillColor = 'transparent';
    scoreValue.style.backgroundClip = 'text';
    
    // Update detail cards
    confidenceValue.textContent = data.confidence ? `${(data.confidence * 100).toFixed(0)}%` : '--';
    
    if (data.component_scores) {
        techHiringValue.textContent = `${data.component_scores.tech_hiring || 0}/100`;
        aiMentionsValue.textContent = `${data.component_scores.ai_mentions || 0}/100`;
        industryValue.textContent = `${data.component_scores.industry_adoption || 0}/100`;
    }
    
    // Re-enable form
    analyzeBtn.disabled = false;
    companyNameInput.disabled = false;
    companyDomainInput.disabled = false;
}

// Download PDF report
async function downloadPdfReport() {
    if (!currentAnalysisData) {
        showError('No analysis data available');
        return;
    }
    
    const companyName = companyNameInput.value.trim();
    const companyDomain = companyDomainInput.value.trim();
    
    const requestData = {
        name: companyName
    };
    
    if (companyDomain) {
        requestData.domain = companyDomain;
    }
    
    try {
        downloadPdfBtn.disabled = true;
        downloadPdfBtn.textContent = '⏳ Generating PDF...';
        
        const response = await fetch('/generate-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error('PDF generation failed');
        }
        
        // Get the blob
        const blob = await response.blob();
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${companyName.replace(/\s+/g, '_')}_AI_Readiness_Report.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        downloadPdfBtn.textContent = '✅ Downloaded!';
        setTimeout(() => {
            downloadPdfBtn.textContent = '📄 Download PDF Report';
            downloadPdfBtn.disabled = false;
        }, 2000);
        
    } catch (error) {
        console.error('PDF download error:', error);
        showError('Failed to generate PDF report');
        downloadPdfBtn.textContent = '📄 Download PDF Report';
        downloadPdfBtn.disabled = false;
    }
}

// Start new analysis
function startNewAnalysis() {
    // Reset form
    resetForm();
    
    // Hide results
    resultsSection.style.display = 'none';
    
    // Clear current data
    currentAnalysisData = null;
}

// Reset form
function resetForm() {
    form.reset();
    hideError();
    hideProgress();
    resultsSection.style.display = 'none';
    currentAnalysisData = null;
    
    // Re-enable form elements
    analyzeBtn.disabled = false;
    companyNameInput.disabled = false;
    companyDomainInput.disabled = false;
}

// Hide progress section
function hideProgress() {
    progressSection.style.display = 'none';
    progressBar.style.width = '0%';
}

// Show error message
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(hideError, 5000);
}

// Hide error message
function hideError() {
    errorMessage.style.display = 'none';
    errorMessage.textContent = '';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Setup WebSocket connection
    setupWebSocket();
    
    // Add example companies on click
    const exampleCompanies = [
        { name: 'Google', domain: 'google.com' },
        { name: 'Microsoft', domain: 'microsoft.com' },
        { name: 'JPMorgan Chase', domain: 'jpmorganchase.com' }
    ];
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter to submit
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            if (!analyzeBtn.disabled) {
                form.dispatchEvent(new Event('submit'));
            }
        }
        
        // Escape to reset
        if (e.key === 'Escape') {
            resetForm();
        }
    });
});