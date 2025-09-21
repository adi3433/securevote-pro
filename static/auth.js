// SecureVote Pro - Authentication JavaScript with 2FA

let currentLoginData = {};
let otpTimer = null;

document.addEventListener('DOMContentLoaded', function() {
    setupLoginForm();
    setupOTPForm();
    initializeParticles();
});

function setupLoginForm() {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Show email field for voters
    const usernameField = document.getElementById('username');
    if (usernameField) {
        usernameField.addEventListener('input', function() {
            const emailField = document.getElementById('email-field');
            const username = this.value.toLowerCase();
            
            // Show email field only for voters (not admin or election_commissioner)
            if (username && !username.includes('admin') && !username.includes('commissioner')) {
                emailField.classList.remove('hidden');
                document.getElementById('email').required = true;
            } else {
                emailField.classList.add('hidden');
                document.getElementById('email').required = false;
            }
        });
    }
}

function setupOTPForm() {
    const otpForm = document.getElementById('otp-form');
    const backButton = document.getElementById('back-to-login');
    const resendButton = document.getElementById('resend-otp');
    
    if (otpForm) {
        otpForm.addEventListener('submit', handleOTPVerification);
    }
    
    if (backButton) {
        backButton.addEventListener('click', showLoginForm);
    }
    
    if (resendButton) {
        resendButton.addEventListener('click', resendOTP);
    }
    
    // Auto-format OTP input
    const otpInput = document.getElementById('otp-code');
    if (otpInput) {
        otpInput.addEventListener('input', function() {
            this.value = this.value.replace(/\D/g, '').substring(0, 6);
        });
    }
}

async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const email = document.getElementById('email').value;
    const resultDiv = document.getElementById('login-result');
    const submitBtn = document.querySelector('#login-form button[type="submit"]');
    
    if (!username || !password) {
        showMessage(resultDiv, 'Please enter both username and password', 'error');
        return;
    }
    
    // Check if email is required for voters
    const isVoter = !username.toLowerCase().includes('admin') && !username.toLowerCase().includes('commissioner');
    if (isVoter && !email) {
        showMessage(resultDiv, 'Email address is required for voter authentication', 'error');
        return;
    }
    
    const originalContent = showLoading(submitBtn, 'Authenticating...');
    
    try {
        resultDiv.innerHTML = '';
        showMessage(resultDiv, 'Authenticating...', 'info');
        
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password,
                email: email || null
            })
        });

        const result = await response.json();
        
        if (response.ok) {
            if (result.requires_2fa) {
                // Store login data for OTP verification
                currentLoginData = {
                    username: username,
                    email: email,
                    temp_token: result.temp_token
                };
                
                showOTPForm(email, result.dev_otp);
                showMessage(resultDiv, result.message, 'success');
            } else {
                // Direct login for admin/commissioner
                completeLogin(result);
            }
        } else {
            showMessage(resultDiv, result.detail || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showMessage(resultDiv, 'Network error. Please try again.', 'error');
    } finally {
        hideLoading(submitBtn, originalContent);
    }
}

async function handleOTPVerification(event) {
    event.preventDefault();
    
    const otpCode = document.getElementById('otp-code').value;
    const resultDiv = document.getElementById('login-result');
    const submitBtn = document.querySelector('#otp-form button[type="submit"]');
    
    if (!otpCode || otpCode.length !== 6) {
        showMessage(resultDiv, 'Please enter a valid 6-digit OTP code', 'error');
        return;
    }
    
    const originalContent = showLoading(submitBtn, 'Verifying...');
    
    try {
        const response = await fetch('/auth/verify-otp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: currentLoginData.email,
                otp_code: otpCode,
                temp_token: currentLoginData.temp_token
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            completeLogin(result);
        } else {
            showMessage(resultDiv, result.detail || 'OTP verification failed', 'error');
        }
    } catch (error) {
        console.error('OTP verification error:', error);
        showMessage(resultDiv, 'Network error. Please try again.', 'error');
    } finally {
        hideLoading(submitBtn, originalContent);
    }
}

function completeLogin(result) {
    const resultDiv = document.getElementById('login-result');
    
    // Store authentication data
    localStorage.setItem('access_token', result.access_token);
    localStorage.setItem('user_role', result.role);
    localStorage.setItem('user_name', result.username);
    
    showMessage(resultDiv, 'Login successful! Redirecting...', 'success');
    
    // Redirect based on role
    setTimeout(() => {
        if (result.role === 'admin') {
            window.location.href = '/admin';
        } else if (result.role === 'voter') {
            window.location.href = '/voter';
        } else {
            window.location.href = '/';
        }
    }, 1000);
}

function showOTPForm(email, devOTP = null) {
    document.getElementById('login-form').classList.add('hidden');
    document.getElementById('otp-form-container').classList.remove('hidden');
    document.getElementById('otp-email-display').textContent = email;
    
    // Show dev OTP in development mode
    if (devOTP) {
        const resultDiv = document.getElementById('login-result');
        showMessage(resultDiv, `Development Mode - OTP: ${devOTP}`, 'info');
    }
    
    // Start countdown timer
    startOTPTimer();
    
    // Focus on OTP input
    document.getElementById('otp-code').focus();
}

function showLoginForm() {
    document.getElementById('otp-form-container').classList.add('hidden');
    document.getElementById('login-form').classList.remove('hidden');
    document.getElementById('login-result').innerHTML = '';
    
    // Clear OTP form
    document.getElementById('otp-code').value = '';
    
    // Stop timer
    if (otpTimer) {
        clearInterval(otpTimer);
        otpTimer = null;
    }
}

function startOTPTimer() {
    let timeLeft = 300; // 5 minutes
    const timerElement = document.getElementById('otp-timer');
    
    if (otpTimer) {
        clearInterval(otpTimer);
    }
    
    otpTimer = setInterval(() => {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        if (timeLeft <= 0) {
            clearInterval(otpTimer);
            timerElement.textContent = 'Expired';
            timerElement.className = 'text-red-300 font-medium';
        }
        
        timeLeft--;
    }, 1000);
}

async function resendOTP() {
    const resultDiv = document.getElementById('login-result');
    const resendButton = document.getElementById('resend-otp');
    
    const originalContent = showLoading(resendButton, '');
    
    try {
        const response = await fetch('/auth/resend-otp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: currentLoginData.email,
                username: currentLoginData.username
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage(resultDiv, 'New OTP sent to your email', 'success');
            if (result.dev_otp) {
                showMessage(resultDiv, `Development Mode - New OTP: ${result.dev_otp}`, 'info');
            }
            startOTPTimer(); // Restart timer
        } else {
            showMessage(resultDiv, result.detail || 'Failed to resend OTP', 'error');
        }
    } catch (error) {
        console.error('Resend OTP error:', error);
        showMessage(resultDiv, 'Network error. Please try again.', 'error');
    } finally {
        hideLoading(resendButton, originalContent);
    }
}

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
