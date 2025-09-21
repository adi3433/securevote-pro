// SecureVote Pro - Admin Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    setupEventListeners();
    initializeParticles();
    showSection('voters');
});

function checkAuth() {
    const token = localStorage.getItem('access_token');
    const role = localStorage.getItem('user_role');
    const userName = localStorage.getItem('user_name');
    
    if (!token || role !== 'admin') {
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
    
    // Proof form
    const proofForm = document.getElementById('proof-form');
    if (proofForm) {
        proofForm.addEventListener('submit', handleGenerateProof);
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

async function handleRegisterVoters(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('voter-file');
    const resultDiv = document.getElementById('register-result');
    const submitBtn = document.querySelector('#register-form button[type="submit"]');
    
    if (!fileInput.files[0]) {
        showMessage(resultDiv, 'Please select a CSV file', 'error');
        return;
    }

    const originalContent = showLoading(submitBtn);
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        resultDiv.innerHTML = '';
        showMessage(resultDiv, 'Registering voters...', 'info');
        
        const response = await makeAuthenticatedRequest('/admin/register-voters', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        
        if (response.ok) {
            const registerSuccessHtml = `
                <div class="mt-4">
                    <div class="bg-black/20 rounded-lg p-4 border border-green-400/30">
                        <h4 class="text-green-300 font-semibold mb-2">👥 Voter Registration Complete!</h4>
                        <div class="grid grid-cols-3 gap-4 text-sm">
                            <div class="text-center">
                                <div class="text-2xl font-bold text-blue-300">${result.registered_count}</div>
                                <div class="text-white/70">Registered</div>
                            </div>
                            <div class="text-center">
                                <div class="text-2xl font-bold text-yellow-300">${result.duplicate_count}</div>
                                <div class="text-white/70">Duplicates</div>
                            </div>
                            <div class="text-center">
                                <div class="text-2xl font-bold text-purple-300">${result.total_voters}</div>
                                <div class="text-white/70">Total Voters</div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            showMessage(resultDiv, 
                `✅ Registration Successful!` + registerSuccessHtml, 'success');
        } else {
            showMessage(resultDiv, result.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        showMessage(resultDiv, `Error: ${error.message}`, 'error');
    } finally {
        hideLoading(submitBtn, originalContent);
    }
}

async function handleIssueOTACs(event) {
    event.preventDefault();
    
    const voterIdsInput = document.getElementById('voter-ids');
    const resultDiv = document.getElementById('otac-result');
    const submitBtn = document.querySelector('#otac-form button[type="submit"]');
    
    const voterIds = voterIdsInput.value.split(',').map(id => id.trim()).filter(id => id);
    
    if (voterIds.length === 0) {
        showMessage(resultDiv, 'Please enter voter IDs', 'error');
        return;
    }

    const originalContent = showLoading(submitBtn);

    try {
        resultDiv.innerHTML = '';
        showMessage(resultDiv, 'Issuing OTACs...', 'info');
        
        const response = await makeAuthenticatedRequest('/admin/issue-otacs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({voter_ids: voterIds})
        });

        const result = await response.json();
        
        if (response.ok && result.success) {
            let otacList = `
                <div class="mt-4">
                    <div class="bg-black/20 rounded-lg p-4 border border-green-400/30">
                        <h4 class="text-green-300 font-semibold mb-3">🔑 Generated OTACs:</h4>
                        <div class="space-y-3">
            `;
            
            for (const otacData of result.otacs) {
                otacList += `
                    <div class="bg-black/20 rounded-lg p-3 border border-white/10">
                        <div class="text-white/80 text-sm mb-1">Voter: <strong class="text-white">${otacData.voter_id}</strong></div>
                        <div class="bg-gray-900 rounded px-3 py-2 font-mono text-green-300 text-sm break-all">${otacData.otac}</div>
                    </div>
                `;
            }
            otacList += '</div></div>';
            
            showMessage(resultDiv, 
                `✅ Successfully issued ${result.issued_count} OTACs` + otacList, 'success');
        } else {
            showMessage(resultDiv, result.detail || 'OTAC issuance failed', 'error');
        }
    } catch (error) {
        showMessage(resultDiv, `Error: ${error.message}`, 'error');
    } finally {
        hideLoading(submitBtn, originalContent);
    }
}

async function handleGenerateProof(event) {
    event.preventDefault();
    
    const ballotHash = document.getElementById('ballot-hash').value.trim();
    const resultDiv = document.getElementById('proof-result');
    
    if (!ballotHash) {
        showMessage(resultDiv, 'Please enter a ballot hash', 'error');
        return;
    }

    try {
        resultDiv.innerHTML = '';
        showMessage(resultDiv, 'Generating proof...', 'info');
        
        const response = await makeAuthenticatedRequest('/admin/generate-proof/' + encodeURIComponent(ballotHash));
        const result = await response.json();
        
        if (response.ok) {
            displayProof(result);
        } else {
            showMessage(resultDiv, result.detail || 'Proof generation failed', 'error');
        }
    } catch (error) {
        showMessage(resultDiv, `Error: ${error.message}`, 'error');
    }
}

function displayProof(proofData) {
    const container = document.getElementById('proof-result');
    
    const proofHtml = `
        <div class="bg-black/20 rounded-lg p-6 border border-blue-400/30 mt-4">
            <h4 class="text-blue-300 font-semibold mb-4 flex items-center">
                <i class="fas fa-certificate mr-2"></i>Merkle Proof Generated
            </h4>
            <div class="space-y-4 text-sm">
                <div>
                    <span class="text-white/70">Ballot Hash:</span>
                    <div class="bg-gray-900 rounded px-3 py-2 font-mono text-blue-300 text-xs break-all mt-1">${proofData.ballot_hash}</div>
                </div>
                <div>
                    <span class="text-white/70">Merkle Root:</span>
                    <div class="bg-gray-900 rounded px-3 py-2 font-mono text-green-300 text-xs break-all mt-1">${proofData.merkle_root}</div>
                </div>
                <div>
                    <span class="text-white/70">Proof Path:</span>
                    <div class="bg-gray-900 rounded px-3 py-2 mt-1 max-h-32 overflow-y-auto">
                        ${proofData.proof.map(p => `<div class="font-mono text-purple-300 text-xs break-all">${p}</div>`).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    showMessage(container, '✅ Proof Generated Successfully!' + proofHtml, 'success');
}

async function loadResults() {
    try {
        const response = await makeAuthenticatedRequest('/admin/results');
        const data = await response.json();
        
        if (response.ok) {
            updateResultsChart(data.results);
            updateResultsTable(data.results);
            document.getElementById('merkle-root').textContent = data.merkle_root || 'No votes cast yet';
        }
    } catch (error) {
        console.error('Failed to load results:', error);
    }
}

async function loadAuditTrail() {
    try {
        const response = await makeAuthenticatedRequest('/admin/audit-trail');
        const data = await response.json();
        
        if (response.ok) {
            displayAuditTrail(data.events);
        }
    } catch (error) {
        console.error('Failed to load audit trail:', error);
    }
}

function updateResultsChart(results) {
    const ctx = document.getElementById('results-chart').getContext('2d');
    
    if (window.resultsChart) {
        window.resultsChart.destroy();
    }
    
    window.resultsChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: results.map(r => r.candidate_id),
            datasets: [{
                data: results.map(r => r.vote_count),
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 101, 101, 0.8)',
                    'rgba(139, 92, 246, 0.8)'
                ],
                borderColor: [
                    'rgb(59, 130, 246)',
                    'rgb(16, 185, 129)',
                    'rgb(245, 101, 101)',
                    'rgb(139, 92, 246)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: 'white'
                    }
                }
            }
        }
    });
}

function updateResultsTable(results) {
    const container = document.getElementById('results-table');
    const totalVotes = results.reduce((sum, r) => sum + r.vote_count, 0);
    
    let tableHtml = '';
    results.forEach(result => {
        const percentage = totalVotes > 0 ? ((result.vote_count / totalVotes) * 100).toFixed(1) : 0;
        tableHtml += `
            <div class="bg-black/20 rounded-lg p-4 border border-white/10">
                <div class="flex justify-between items-center mb-2">
                    <span class="text-white font-medium">${result.candidate_id}</span>
                    <span class="text-blue-300 font-bold">${result.vote_count} votes</span>
                </div>
                <div class="w-full bg-gray-700 rounded-full h-2">
                    <div class="bg-blue-500 h-2 rounded-full" style="width: ${percentage}%"></div>
                </div>
                <div class="text-right text-white/70 text-sm mt-1">${percentage}%</div>
            </div>
        `;
    });
    
    container.innerHTML = tableHtml;
}

function displayAuditTrail(events) {
    const container = document.getElementById('audit-trail');
    
    let eventsHtml = '';
    events.forEach(event => {
        let eventData;
        try {
            eventData = typeof event.details === 'string' ? JSON.parse(event.details) : event.details;
        } catch (e) {
            eventData = event.details || {};
        }
        
        eventsHtml += `
            <div class="bg-black/20 rounded-lg p-4 border border-white/10">
                <div class="flex justify-between items-start mb-2">
                    <span class="px-3 py-1 rounded-full text-xs font-medium ${getEventTypeColor(event.type)}">${event.type}</span>
                    <span class="text-white/70 text-sm">${new Date(event.timestamp).toLocaleString('en-IN', {timeZone: 'Asia/Kolkata'})}</span>
                </div>
                <div class="text-white/80 text-sm space-y-1">
                    ${formatEventDetails(event.type, eventData)}
                </div>
                ${event.prev_root && event.new_root ? `
                    <div class="mt-3 pt-3 border-t border-white/10">
                        <div class="text-xs text-white/60">
                            <div>Previous Root: <span class="font-mono text-purple-300">${event.prev_root.substring(0, 16)}...</span></div>
                            <div>New Root: <span class="font-mono text-green-300">${event.new_root.substring(0, 16)}...</span></div>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    });
    
    container.innerHTML = eventsHtml || '<div class="text-white/60 text-center py-8">No audit events found</div>';
}

function formatEventDetails(type, details) {
    switch(type) {
        case 'CAST':
            return `
                <div><strong>Candidate:</strong> ${details.candidate_id || 'N/A'}</div>
                <div><strong>Ballot Hash:</strong> <span class="font-mono text-green-300">${(details.ballot_hash || '').substring(0, 20)}...</span></div>
                <div><strong>Sequence:</strong> ${details.seq || 'N/A'}</div>
            `;
        case 'REGISTER_VOTERS':
            return `<div><strong>Voters Registered:</strong> ${details.count || 'N/A'}</div>`;
        case 'ISSUE_OTACS':
            return `<div><strong>OTACs Issued:</strong> ${details.count || 'N/A'}</div>`;
        default:
            return `<div class="font-mono text-xs">${JSON.stringify(details, null, 2)}</div>`;
    }
}

// Download audit trail as CSV
function downloadAuditTrail() {
    const token = localStorage.getItem('access_token');
    
    fetch('/admin/audit-trail', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.events && data.events.length > 0) {
            const csvContent = convertAuditTrailToCSV(data.events);
            downloadCSV(csvContent, `audit_trail_${new Date().toISOString().split('T')[0]}.csv`);
        } else {
            alert('No audit events to download');
        }
    })
    .catch(error => {
        console.error('Error downloading audit trail:', error);
        alert('Failed to download audit trail');
    });
}

function convertAuditTrailToCSV(events) {
    const headers = ['ID', 'Type', 'Timestamp', 'Details', 'Previous Root', 'New Root'];
    let csvContent = headers.join(',') + '\n';
    
    events.forEach(event => {
        let details = '';
        try {
            const eventData = typeof event.details === 'string' ? JSON.parse(event.details) : event.details;
            details = JSON.stringify(eventData).replace(/"/g, '""');
        } catch (e) {
            details = String(event.details || '').replace(/"/g, '""');
        }
        
        const row = [
            event.id || '',
            event.type || '',
            new Date(event.timestamp).toLocaleString('en-IN', {timeZone: 'Asia/Kolkata'}),
            `"${details}"`,
            event.prev_root || '',
            event.new_root || ''
        ];
        csvContent += row.join(',') + '\n';
    });
    
    return csvContent;
}

function downloadCSV(csvContent, filename) {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

function getEventTypeColor(type) {
    const colors = {
        'REGISTER_VOTERS': 'bg-blue-900/30 text-blue-300 border border-blue-400/30',
        'ISSUE_OTACS': 'bg-green-900/30 text-green-300 border border-green-400/30',
        'CAST': 'bg-purple-900/30 text-purple-300 border border-purple-400/30',
        'UNDO': 'bg-red-900/30 text-red-300 border border-red-400/30'
    };
    
    return colors[type] || 'bg-gray-900/30 text-gray-300 border border-gray-400/30';
}

// Ballot hash lookup function
async function lookupBallot() {
    const ballotHash = document.getElementById('ballot-hash').value.trim();
    const resultDiv = document.getElementById('proof-result');
    
    if (!ballotHash) {
        showMessage(resultDiv, 'Please enter a ballot hash', 'error');
        return;
    }
    
    const token = localStorage.getItem('access_token');
    
    try {
        const response = await fetch(`/admin/ballot-lookup/${ballotHash}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const result = await response.json();
        
        if (response.ok && result.found) {
            resultDiv.innerHTML = `
                <div class="bg-green-900/20 border border-green-400/30 rounded-lg p-6">
                    <h4 class="text-green-300 font-semibold mb-4 flex items-center">
                        <i class="fas fa-check-circle mr-2"></i>Ballot Found & Verified
                    </h4>
                    <div class="space-y-3 text-sm">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <span class="text-white/70">Sequence Number:</span>
                                <div class="text-white font-mono">#${result.ballot.seq}</div>
                            </div>
                            <div>
                                <span class="text-white/70">Candidate:</span>
                                <div class="text-green-300 font-semibold">${result.ballot.candidate_id}</div>
                            </div>
                        </div>
                        <div>
                            <span class="text-white/70">Timestamp:</span>
                            <div class="text-white">${new Date(result.ballot.timestamp).toLocaleString('en-IN', {timeZone: 'Asia/Kolkata'})}</div>
                        </div>
                        <div>
                            <span class="text-white/70">Full Ballot Hash:</span>
                            <div class="bg-gray-900 rounded px-3 py-2 font-mono text-green-300 text-xs break-all mt-1">${result.ballot.ballot_hash}</div>
                        </div>
                        <div class="mt-4 p-3 bg-blue-900/20 rounded border border-blue-400/30">
                            <div class="flex items-center text-blue-300 text-sm">
                                <i class="fas fa-shield-check mr-2"></i>
                                This ballot is cryptographically verified and part of the Merkle tree.
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            showMessage(resultDiv, result.error || 'Ballot hash not found in the system', 'error');
        }
    } catch (error) {
        console.error('Error looking up ballot:', error);
        showMessage(resultDiv, 'Failed to lookup ballot hash', 'error');
    }
}

// Navigation and UI functions (reused from main app)
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
    });
    
    // Show selected section
    const targetSection = document.getElementById(sectionName + '-section');
    if (targetSection) {
        targetSection.classList.remove('hidden');
    }
    
    // Update navigation - find the correct button by data attribute or onclick
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
        btn.classList.add('text-white/70');
    });
    
    // Find and activate the correct navigation button
    const activeBtn = document.querySelector(`[onclick="showSection('${sectionName}')"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
        activeBtn.classList.remove('text-white/70');
    }
    
    // Load data for specific sections
    if (sectionName === 'results') {
        loadResults();
    } else if (sectionName === 'audit') {
        loadAuditTrail();
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
