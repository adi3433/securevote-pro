// SecureVote Pro - Core JavaScript Functions

// Global state management
let currentSection = 'admin';
let resultsChart = null;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeParticles();
    showSection('admin');
    setupEventListeners();
});

// Particle animation system
function initializeParticles() {
    const particlesContainer = document.getElementById('particles');
    const particleCount = 50;
    
    for (let i = 0; i < particleCount; i++) {
        createParticle(particlesContainer);
    }
    
    setInterval(() => {
        if (particlesContainer.children.length < particleCount) {
            createParticle(particlesContainer);
        }
    }, 500);
}

function createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    
    const size = Math.random() * 4 + 2;
    particle.style.width = size + 'px';
    particle.style.height = size + 'px';
    particle.style.left = Math.random() * 100 + '%';
    particle.style.animationDelay = Math.random() * 25 + 's';
    particle.style.animationDuration = (Math.random() * 10 + 20) + 's';
    
    container.appendChild(particle);
    
    setTimeout(() => {
        if (particle.parentNode) {
            particle.parentNode.removeChild(particle);
        }
    }, 30000);
}

// Navigation system
function showSection(sectionName) {
    // Hide all sections
    const sections = ['admin-section', 'voter-section', 'results-section', 'audit-section'];
    sections.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.classList.add('hidden');
        }
    });
    
    // Show selected section
    const targetSection = document.getElementById(sectionName + '-section');
    if (targetSection) {
        targetSection.classList.remove('hidden');
        currentSection = sectionName;
    }
    
    // Update navigation buttons
    updateNavButtons(sectionName);
}

function updateNavButtons(activeSection) {
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
        btn.classList.remove('active');
    });
    
    const sectionMap = {
        'admin': 0,
        'voter': 1,
        'results': 2,
        'audit': 3
    };
    
    const activeIndex = sectionMap[activeSection];
    if (activeIndex !== undefined && navButtons[activeIndex]) {
        navButtons[activeIndex].classList.add('active');
    }
}

// Event listeners setup
function setupEventListeners() {
    // Register form
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegisterVoters);
    }
    
    // OTAC form
    const otacForm = document.getElementById('otac-form');
    if (otacForm) {
        otacForm.addEventListener('submit', handleIssueOTACs);
    }
    
    // Vote form
    const voteForm = document.getElementById('vote-form');
    if (voteForm) {
        voteForm.addEventListener('submit', handleCastVote);
    }
    
    // Proof form
    const proofForm = document.getElementById('proof-form');
    if (proofForm) {
        proofForm.addEventListener('submit', handleGenerateProof);
    }
}

// Message display utilities
function showMessage(containerId, type, title, content, hash = null) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const messageClass = type === 'success' ? 'success-message' : 
                        type === 'error' ? 'error-message' : 'info-message';
    
    const icon = type === 'success' ? 'fas fa-check-circle' : 
                type === 'error' ? 'fas fa-exclamation-triangle' : 'fas fa-info-circle';
    
    let hashDisplay = '';
    if (hash) {
        hashDisplay = `
            <div class="mt-4 p-4 bg-black/20 rounded-lg">
                <div class="flex items-center mb-2">
                    <i class="fas fa-fingerprint text-emerald-400 mr-2"></i>
                    <span class="font-semibold text-white">Ballot Hash:</span>
                </div>
                <p class="font-mono text-sm text-emerald-300 break-all">${hash}</p>
            </div>
        `;
    }
    
    container.innerHTML = `
        <div class="${messageClass} p-6 rounded-2xl text-white mb-4" style="display: block !important; visibility: visible !important;">
            <div class="flex items-start">
                <i class="${icon} text-2xl mr-4 mt-1"></i>
                <div class="flex-1">
                    <h4 class="font-bold text-lg mb-2">${title}</h4>
                    <p class="text-white/90">${content}</p>
                    ${hashDisplay}
                </div>
            </div>
        </div>
    `;
    
    container.style.display = 'block';
    container.style.visibility = 'visible';
}

function showLoading(button, text = 'Processing...') {
    const originalContent = button.innerHTML;
    button.innerHTML = `
        <div class="loading-spinner"></div>
        <span>${text}</span>
    `;
    button.disabled = true;
    return originalContent;
}

function hideLoading(button, originalContent) {
    button.innerHTML = originalContent;
    button.disabled = false;
}

// API interaction functions
async function makeRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Request failed:', error);
        throw error;
    }
}

// Form handlers
async function handleRegisterVoters(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('voter-file');
    const submitButton = event.target.querySelector('button[type="submit"]');
    
    if (!fileInput.files[0]) {
        showMessage('register-result', 'error', 'File Required', 'Please select a CSV file to upload.');
        return;
    }
    
    const originalContent = showLoading(submitButton, 'Registering Voters...');
    
    try {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        const response = await fetch('/register-voters', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('register-result', 'success', 'Registration Complete', 
                       `Successfully registered ${result.count} voters.`);
            fileInput.value = '';
        } else {
            showMessage('register-result', 'error', 'Registration Failed', 
                       result.error || 'An error occurred during registration.');
        }
    } catch (error) {
        showMessage('register-result', 'error', 'Network Error', 
                   'Failed to connect to server. Please try again.');
    } finally {
        hideLoading(submitButton, originalContent);
    }
}

async function handleIssueOTACs(event) {
    event.preventDefault();
    
    const voterIdsInput = document.getElementById('voter-ids');
    const submitButton = event.target.querySelector('button[type="submit"]');
    
    const voterIds = voterIdsInput.value.trim();
    if (!voterIds) {
        showMessage('otac-result', 'error', 'Input Required', 'Please enter voter IDs.');
        return;
    }
    
    const originalContent = showLoading(submitButton, 'Generating OTACs...');
    
    try {
        const result = await makeRequest('/issue-otacs', {
            method: 'POST',
            body: JSON.stringify({
                voter_ids: voterIds.split(',').map(id => id.trim())
            })
        });
        
        if (result.success) {
            let otacList = result.otacs.map(otac => 
                `<div class="flex justify-between items-center p-3 bg-black/20 rounded-lg">
                    <span class="font-mono text-sm">${otac.voter_id}</span>
                    <span class="font-mono text-emerald-300">${otac.otac}</span>
                </div>`
            ).join('');
            
            showMessage('otac-result', 'success', 'OTACs Generated', 
                       `Generated ${result.otacs.length} access codes:<div class="mt-4 space-y-2">${otacList}</div>`);
            voterIdsInput.value = '';
        } else {
            showMessage('otac-result', 'error', 'Generation Failed', 
                       result.error || 'Failed to generate OTACs.');
        }
    } catch (error) {
        showMessage('otac-result', 'error', 'Network Error', 
                   'Failed to connect to server. Please try again.');
    } finally {
        hideLoading(submitButton, originalContent);
    }
}

async function handleCastVote(event) {
    event.preventDefault();
    
    const otacInput = document.getElementById('otac');
    const candidateSelect = document.getElementById('candidate');
    const submitButton = event.target.querySelector('button[type="submit"]');
    
    const otac = otacInput.value.trim();
    const candidate = candidateSelect.value;
    
    if (!otac || !candidate) {
        showMessage('vote-result', 'error', 'Missing Information', 
                   'Please enter your OTAC and select a candidate.');
        return;
    }
    
    const originalContent = showLoading(submitButton, 'Casting Vote...');
    
    try {
        const result = await makeRequest('/cast-vote', {
            method: 'POST',
            body: JSON.stringify({
                otac: otac,
                candidate_id: candidate
            })
        });
        
        if (result.success) {
            showMessage('vote-result', 'success', 'Vote Cast Successfully', 
                       'Your vote has been recorded and verified.', result.ballot_hash);
            otacInput.value = '';
            candidateSelect.value = '';
        } else {
            showMessage('vote-result', 'error', 'Vote Failed', 
                       result.error || 'Failed to cast vote.');
        }
    } catch (error) {
        showMessage('vote-result', 'error', 'Network Error', 
                   'Failed to connect to server. Please try again.');
    } finally {
        hideLoading(submitButton, originalContent);
    }
}

async function handleGenerateProof(event) {
    event.preventDefault();
    
    const hashInput = document.getElementById('ballot-hash');
    const submitButton = event.target.querySelector('button[type="submit"]');
    
    const ballotHash = hashInput.value.trim();
    if (!ballotHash) {
        showMessage('proof-result', 'error', 'Hash Required', 'Please enter a ballot hash.');
        return;
    }
    
    const originalContent = showLoading(submitButton, 'Generating Proof...');
    
    try {
        const result = await makeRequest(`/generate-proof/${ballotHash}`);
        
        if (result.success) {
            const proofDisplay = `
                <div class="space-y-3">
                    <div class="p-4 bg-black/20 rounded-lg">
                        <div class="font-semibold text-emerald-400 mb-2">Merkle Proof:</div>
                        <div class="font-mono text-sm text-white break-all">${result.proof.join('<br>')}</div>
                    </div>
                    <div class="p-4 bg-black/20 rounded-lg">
                        <div class="font-semibold text-emerald-400 mb-2">Root Hash:</div>
                        <div class="font-mono text-sm text-white break-all">${result.root}</div>
                    </div>
                </div>
            `;
            
            showMessage('proof-result', 'success', 'Proof Generated', 
                       `Cryptographic proof verified:${proofDisplay}`);
        } else {
            showMessage('proof-result', 'error', 'Proof Failed', 
                       result.error || 'Failed to generate proof.');
        }
    } catch (error) {
        showMessage('proof-result', 'error', 'Network Error', 
                   'Failed to connect to server. Please try again.');
    } finally {
        hideLoading(submitButton, originalContent);
    }
}

// Global functions for window access
window.showSection = showSection;
window.loadStats = loadStats;
window.loadResults = loadResults;
window.loadAuditTrail = loadAuditTrail;
window.undoLast = undoLast;

// Placeholder functions for future implementation
async function loadStats() {
    console.log('Loading stats...');
}

async function loadResults() {
    console.log('Loading results...');
}

async function loadAuditTrail() {
    console.log('Loading audit trail...');
}

async function undoLast() {
    console.log('Undoing last action...');
}
