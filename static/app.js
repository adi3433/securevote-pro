// SecureVote Pro - Enhanced JavaScript Functions v2.0
let currentChart = null;

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
});

function setupEventListeners() {
    // Register voters form
    document.getElementById('register-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        await registerVoters();
    });

    // Issue OTACs form
    document.getElementById('otac-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        await issueOTACs();
    });

    // Vote form
    document.getElementById('vote-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        await castVote();
    });

    // Proof form
    document.getElementById('proof-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        await getProof();
    });
}

// Enhanced register voters with loading states
async function registerVoters() {
    const fileInput = document.getElementById('voter-file');
    const resultDiv = document.getElementById('register-result');
    const submitBtn = document.querySelector('#register-form button[type="submit"]');
    
    if (!fileInput.files[0]) {
        showMessage(document.getElementById('register-result'), 'Please select a CSV file', 'error');
        return;
    }

    const originalContent = showLoading(submitBtn);
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        // Clear any previous messages first
        const resultDiv = document.getElementById('register-result');
        resultDiv.innerHTML = '';
        
        showMessage(resultDiv, 'Registering voters...', 'info');
        
        const response = await fetch('/api/registerVoters', {
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

// Issue OTACs
async function issueOTACs() {
    const voterIdsInput = document.getElementById('voter-ids');
    const resultDiv = document.getElementById('otac-result');
    
    const voterIds = voterIdsInput.value.split(',').map(id => id.trim()).filter(id => id);
    
    if (voterIds.length === 0) {
        showMessage(document.getElementById('otac-result'), 'Please enter voter IDs', 'error');
        return;
    }

    const submitBtn = document.querySelector('#otac-form button[type="submit"]');
    const originalContent = showLoading(submitBtn);

    try {
        // Clear any previous messages first
        resultDiv.innerHTML = '';
        showMessage(resultDiv, 'Issuing OTACs...', 'info');
        
        const response = await fetch('/api/issueOtacs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({voter_ids: voterIds})
        });

        const result = await response.json();
        
        if (response.ok) {
            let otacList = '<div class="mt-4"><h4 class="font-semibold text-white mb-3">🔑 Generated OTACs:</h4><div class="space-y-2">';
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

// Cast vote
async function castVote() {
    const otac = document.getElementById('otac').value;
    const candidateId = document.getElementById('candidate').value;
    const resultDiv = document.getElementById('vote-result');
    
    if (!otac || !candidateId) {
        showMessage(document.getElementById('vote-result'), 'Please fill in all fields', 'error');
        return;
    }

    const submitBtn = document.querySelector('#vote-form button[type="submit"]');
    const originalContent = showLoading(submitBtn);

    try {
        // Clear any previous messages first
        resultDiv.innerHTML = '';
        showMessage(resultDiv, 'Casting vote...', 'info');
        
        const response = await fetch('/cast-vote', {
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
                <div class="mt-4 space-y-3">
                    <div class="bg-black/20 rounded-lg p-4 border border-green-400/30">
                        <h4 class="text-green-300 font-semibold mb-2">🗳️ Vote Cast Successfully!</h4>
                        <div class="space-y-2 text-sm">
                            <div>
                                <span class="text-white/70">Ballot Hash:</span>
                                <div class="bg-gray-900 rounded px-3 py-2 font-mono text-green-300 text-xs break-all mt-1">${result.ballot_hash}</div>
                            </div>
                            <div>
                                <span class="text-white/70">Sequence:</span>
                                <span class="text-blue-300 font-mono ml-2">#${result.seq}</span>
                            </div>
                            <div>
                                <span class="text-white/70">New Merkle Root:</span>
                                <div class="bg-gray-900 rounded px-3 py-2 font-mono text-purple-300 text-xs break-all mt-1">${result.new_root}</div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            showMessage(resultDiv, 
                `✅ Vote Successfully Recorded!` + voteSuccessHtml, 'success');
            
            // Clear form
            document.getElementById('otac').value = '';
            document.getElementById('candidate').value = '';
        } else {
            showMessage(resultDiv, result.detail || 'Vote casting failed', 'error');
        }
    } catch (error) {
        showMessage(resultDiv, `Error: ${error.message}`, 'error');
    } finally {
        hideLoading(submitBtn, originalContent);
    }
}

// Load results
async function loadResults() {
    try {
        const response = await fetch('/results');
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
            document.getElementById('merkle-root').textContent = data.merkle_root || 'No votes cast yet';
        } else {
            console.error('Failed to load results');
        }
    } catch (error) {
        console.error('Error loading results:', error);
    }
}

// Display results
function displayResults(data) {
    const ctx = document.getElementById('results-chart').getContext('2d');
    const tableDiv = document.getElementById('results-table');
    
    const candidates = Object.keys(data.results);
    const votes = Object.values(data.results);
    
    // Destroy existing chart
    if (currentChart) {
        currentChart.destroy();
    }
    
    // Create new chart
    currentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: candidates.map(c => c.replace('_', ' ').toUpperCase()),
            datasets: [{
                label: 'Votes',
                data: votes,
                backgroundColor: [
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(255, 205, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 205, 86, 1)',
                    'rgba(75, 192, 192, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
    
    // Create table
    let tableHTML = '<table class="w-full border-collapse border border-gray-300">';
    tableHTML += '<thead><tr class="bg-gray-100"><th class="border border-gray-300 px-4 py-2">Candidate</th><th class="border border-gray-300 px-4 py-2">Votes</th></tr></thead>';
    tableHTML += '<tbody>';
    
    for (const [candidate, count] of Object.entries(data.results)) {
        tableHTML += `<tr><td class="border border-gray-300 px-4 py-2">${candidate.replace('_', ' ').toUpperCase()}</td><td class="border border-gray-300 px-4 py-2">${count}</td></tr>`;
    }
    
    tableHTML += `<tr class="bg-gray-50 font-semibold"><td class="border border-gray-300 px-4 py-2">TOTAL</td><td class="border border-gray-300 px-4 py-2">${data.total_votes}</td></tr>`;
    tableHTML += '</tbody></table>';
    
    tableDiv.innerHTML = tableHTML;
}

// Load system stats
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (response.ok) {
            displayStats(data);
        } else {
            console.error('Failed to load stats');
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Display stats
function displayStats(data) {
    const statsDiv = document.getElementById('stats-display');
    
    let html = '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">';
    
    // Basic stats
    html += `
        <div class="bg-blue-50 p-4 rounded">
            <h4 class="font-semibold text-blue-800">Voters</h4>
            <p class="text-2xl font-bold text-blue-600">${data.total_voters}</p>
            <p class="text-sm text-blue-600">Total registered</p>
        </div>
        <div class="bg-green-50 p-4 rounded">
            <h4 class="font-semibold text-green-800">Voted</h4>
            <p class="text-2xl font-bold text-green-600">${data.voted_count}</p>
            <p class="text-sm text-green-600">Votes cast</p>
        </div>
        <div class="bg-purple-50 p-4 rounded">
            <h4 class="font-semibold text-purple-800">Remaining</h4>
            <p class="text-2xl font-bold text-purple-600">${data.remaining_voters}</p>
            <p class="text-sm text-purple-600">Can still vote</p>
        </div>
    `;
    
    // Merkle tree stats
    if (data.merkle_stats) {
        html += `
            <div class="bg-orange-50 p-4 rounded">
                <h4 class="font-semibold text-orange-800">Tree Height</h4>
                <p class="text-2xl font-bold text-orange-600">${data.merkle_stats.tree_height}</p>
                <p class="text-sm text-orange-600">Merkle tree levels</p>
            </div>
            <div class="bg-red-50 p-4 rounded">
                <h4 class="font-semibold text-red-800">Proof Size</h4>
                <p class="text-2xl font-bold text-red-600">${data.merkle_stats.proof_size_bytes}</p>
                <p class="text-sm text-red-600">Bytes per proof</p>
            </div>
        `;
    }
    
    // Bloom filter stats
    if (data.bloom_filter_stats) {
        html += `
            <div class="bg-indigo-50 p-4 rounded">
                <h4 class="font-semibold text-indigo-800">Bloom Filter</h4>
                <p class="text-2xl font-bold text-indigo-600">${(data.bloom_filter_stats.current_error_rate * 100).toFixed(2)}%</p>
                <p class="text-sm text-indigo-600">Error rate</p>
            </div>
        `;
    }
    
    html += '</div>';
    
    // Demo mode indicator
    if (data.demo_mode) {
        html += '<div class="mt-4 bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">Demo Mode Active - Undo operations enabled</div>';
    }
    
    statsDiv.innerHTML = html;
}

// Undo last action
async function undoLast() {
    const resultDiv = document.getElementById('undo-result');
    
    try {
        showMessage(resultDiv, 'Undoing last action...', 'info');
        
        const response = await fetch('/api/undoLast', {
            method: 'POST'
        });

        const result = await response.json();
        
        if (response.ok) {
            showMessage(resultDiv, 
                `Successfully undone: ${result.undone_action}. ` +
                `New Merkle root: ${result.new_root}`, 'success');
        } else {
            showMessage(resultDiv, result.detail || 'Undo failed', 'error');
        }
    } catch (error) {
        showMessage(resultDiv, `Error: ${error.message}`, 'error');
    }
}

// Load audit trail
async function loadAuditTrail() {
    try {
        const response = await fetch('/api/auditTrail');
        const data = await response.json();
        
        if (response.ok) {
            displayAuditTrail(data.events);
        } else {
            console.error('Failed to load audit trail');
        }
    } catch (error) {
        console.error('Error loading audit trail:', error);
    }
}

// Display audit trail
function displayAuditTrail(events) {
    const trailDiv = document.getElementById('audit-trail');
    
    if (events.length === 0) {
        trailDiv.innerHTML = '<p class="text-gray-500">No audit events found.</p>';
        return;
    }
    
    let html = '<div class="space-y-4">';
    
    events.forEach(event => {
        const timestamp = new Date(event.timestamp).toLocaleString();
        const typeColor = getEventTypeColor(event.type);
        
        html += `
            <div class="border border-gray-200 rounded-lg p-4">
                <div class="flex justify-between items-start mb-2">
                    <span class="px-2 py-1 text-xs font-semibold rounded ${typeColor}">${event.type}</span>
                    <span class="text-sm text-gray-500">${timestamp}</span>
                </div>
                <div class="text-sm">
                    <strong>Details:</strong> ${JSON.stringify(event.details, null, 2)}
                </div>
                ${event.prev_root ? `<div class="text-xs text-gray-600 mt-2"><strong>Prev Root:</strong> ${event.prev_root}</div>` : ''}
                ${event.new_root ? `<div class="text-xs text-gray-600"><strong>New Root:</strong> ${event.new_root}</div>` : ''}
            </div>
        `;
    });
    
    html += '</div>';
    trailDiv.innerHTML = html;
}

// Get proof for ballot
async function getProof() {
    const ballotHash = document.getElementById('ballot-hash').value;
    const resultDiv = document.getElementById('proof-result');
    
    if (!ballotHash) {
        showMessage(resultDiv, 'Please enter a ballot hash', 'error');
        return;
    }

    try {
        showMessage(resultDiv, 'Generating proof...', 'info');
        
        const response = await fetch('/generate-proof/' + encodeURIComponent(ballotHash));

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

// Display proof
function displayProof(proofData) {
    const resultDiv = document.getElementById('proof-result');
    
    let html = `
        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 class="font-semibold text-green-800 mb-2">Merkle Inclusion Proof</h4>
            <div class="space-y-2 text-sm">
                <div><strong>Ballot Hash:</strong> <code class="bg-gray-100 px-2 py-1 rounded">${proofData.ballot_hash}</code></div>
                <div><strong>Leaf Index:</strong> ${proofData.leaf_index}</div>
                <div><strong>Tree Size:</strong> ${proofData.tree_size}</div>
                <div><strong>Root:</strong> <code class="bg-gray-100 px-2 py-1 rounded">${proofData.root}</code></div>
                <div><strong>Proof Path:</strong></div>
                <ul class="list-disc list-inside ml-4">
    `;
    
    proofData.proof.forEach((hash, index) => {
        html += `<li><code class="bg-gray-100 px-2 py-1 rounded text-xs">${hash}</code></li>`;
    });
    
    html += `
                </ul>
                <div class="mt-4">
                    <button onclick="verifyProofClient('${proofData.ballot_hash}', ${proofData.leaf_index}, ${JSON.stringify(proofData.proof).replace(/"/g, '&quot;')}, '${proofData.root}')" 
                            class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                        Verify Proof Client-Side
                    </button>
                </div>
            </div>
        </div>
    `;
    
    resultDiv.innerHTML = html;
}

// Client-side proof verification
async function verifyProofClient(leaf, leafIndex, proof, root) {
    try {
        const response = await fetch('/verify-proof', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                leaf: leaf,
                leaf_index: leafIndex,
                proof: proof,
                root: root
            })
        });

        const result = await response.json();
        
        if (response.ok) {
            const message = result.valid ? 'Proof is VALID ✓' : 'Proof is INVALID ✗';
            const color = result.valid ? 'text-green-600' : 'text-red-600';
            
            const verifyDiv = document.createElement('div');
            verifyDiv.className = `mt-2 p-2 rounded ${result.valid ? 'bg-green-100' : 'bg-red-100'}`;
            verifyDiv.innerHTML = `<strong class="${color}">${message}</strong>`;
            
            document.getElementById('proof-result').appendChild(verifyDiv);
        }
    } catch (error) {
        console.error('Verification error:', error);
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

function getEventTypeColor(type) {
    const colors = {
        'REGISTER_VOTERS': 'bg-blue-100 text-blue-800',
        'ISSUE_OTACS': 'bg-green-100 text-green-800',
        'CAST': 'bg-purple-100 text-purple-800',
        'UNDO': 'bg-red-100 text-red-800'
    };
    
    return colors[type] || 'bg-gray-100 text-gray-800';
}
