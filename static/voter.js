// SecureVote Pro - Voter Portal JavaScript

document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    setupEventListeners();
    initializeParticles();
});

function checkAuth() {
    const token = localStorage.getItem('access_token');
    const role = localStorage.getItem('user_role');
    const userName = localStorage.getItem('user_name');
    
    if (!token || role !== 'voter') {
        window.location.href = '/login';
        return;
    }
    
    // Set user name in header
    if (userName) {
        document.getElementById('user-name').textContent = userName;
    }
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_name');
    window.location.href = '/login';
}

function setupEventListeners() {
    const voteForm = document.getElementById('vote-form');
    if (voteForm) {
        voteForm.addEventListener('submit', handleCastVote);
    }
}

async function makeAuthenticatedRequest(url, options = {}) {
    const token = localStorage.getItem('access_token');
    
    const headers = {
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    if (response.status === 401) {
        logout();
        return;
    }
    
    return response;
}

async function handleCastVote(event) {
    event.preventDefault();
    
    const otac = document.getElementById('otac').value;
    const candidateId = document.getElementById('candidate').value;
    const resultDiv = document.getElementById('vote-result');
    const submitBtn = document.querySelector('#vote-form button[type="submit"]');
    
    if (!otac || !candidateId) {
        showMessage(resultDiv, 'Please fill in all fields', 'error');
        return;
    }

    const originalContent = showLoading(submitBtn, 'Casting Vote...');

    try {
        resultDiv.innerHTML = '';
        showMessage(resultDiv, 'Casting vote...', 'info');
        
        const response = await makeAuthenticatedRequest('/voter/cast-vote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                otac: otac,
                candidate_id: candidateId
            })
        });

        const result = await response.json();
        
        if (response.ok) {
            const voteSuccessHtml = `
                <div class="mt-4">
                    <div class="bg-black/20 rounded-lg p-6 border border-green-400/30">
                        <h4 class="text-green-300 font-semibold mb-4 flex items-center">
                            <i class="fas fa-check-circle mr-2"></i>Vote Successfully Recorded!
                        </h4>
                        <div class="space-y-3 text-sm">
                            <div class="flex justify-between">
                                <span class="text-white/70">Ballot Hash:</span>
                                <span class="text-green-300 font-mono text-xs">${result.ballot_hash.substring(0, 16)}...</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-white/70">Timestamp:</span>
                                <span class="text-white">${new Date().toLocaleString('en-IN', {
                                    timeZone: 'Asia/Kolkata',
                                    year: 'numeric',
                                    month: '2-digit',
                                    day: '2-digit',
                                    hour: '2-digit',
                                    minute: '2-digit',
                                    second: '2-digit',
                                    hour12: true
                                })}</span>
                            </div>
                            <div>
                                <span class="text-white/70">New Merkle Root:</span>
                                <div class="bg-gray-900 rounded px-3 py-2 font-mono text-purple-300 text-xs break-all mt-1">${result.new_root}</div>
                            </div>
                        </div>
                        <div class="mt-4 p-3 bg-blue-900/20 rounded border border-blue-400/30">
                            <div class="flex items-center text-blue-300 text-sm">
                                <i class="fas fa-info-circle mr-2"></i>
                                Your vote has been securely recorded and cannot be changed.
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            showMessage(resultDiv, voteSuccessHtml, 'success');
            
            // Clear form
            document.getElementById('otac').value = '';
            document.getElementById('candidate').value = '';
            
            // Disable form to prevent multiple votes
            document.getElementById('vote-form').style.opacity = '0.5';
            document.getElementById('vote-form').style.pointerEvents = 'none';
            
        } else {
            showMessage(resultDiv, result.detail || 'Vote casting failed', 'error');
        }
    } catch (error) {
        showMessage(resultDiv, `Error: ${error.message}`, 'error');
    } finally {
        hideLoading(submitBtn, originalContent);
    }
}

// Utility functions
function showMessage(element, message, type) {
    if (!element) return;
    
    const colors = {
        success: 'bg-green-900/20 border-green-400/30 text-green-300',
        error: 'bg-red-900/20 border-red-400/30 text-red-300',
        info: 'bg-blue-900/20 border-blue-400/30 text-blue-300'
    };
    
    element.innerHTML = `<div class="border px-4 py-3 rounded-lg ${colors[type]} backdrop-blur-sm">${message}</div>`;
    element.style.display = 'block';
}

function showLoading(button, text = 'Processing...') {
    if (!button) return '';
    const originalContent = button.innerHTML;
    button.innerHTML = `
        <div class="flex items-center justify-center space-x-2">
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span>${text}</span>
        </div>
    `;
    button.disabled = true;
    return originalContent;
}

function hideLoading(button, originalContent) {
    if (!button) return;
    button.innerHTML = originalContent;
    button.disabled = false;
}

// Particle animation system (reused from main app)
function initializeParticles() {
    const particlesContainer = document.getElementById('particles');
    if (!particlesContainer) return;
    
    const particleCount = 30;
    
    for (let i = 0; i < particleCount; i++) {
        createParticle(particlesContainer);
    }
    
    setInterval(() => {
        if (particlesContainer.children.length < particleCount) {
            createParticle(particlesContainer);
        }
    }, 1000);
}

function createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    
    const size = Math.random() * 3 + 1;
    particle.style.width = size + 'px';
    particle.style.height = size + 'px';
    particle.style.left = Math.random() * 100 + '%';
    particle.style.animationDelay = Math.random() * 15 + 's';
    particle.style.animationDuration = (Math.random() * 8 + 12) + 's';
    
    container.appendChild(particle);
    
    setTimeout(() => {
        if (particle.parentNode) {
            particle.parentNode.removeChild(particle);
        }
    }, 20000);
}
