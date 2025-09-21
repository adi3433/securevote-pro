"""
Email service for SecureVote Pro - OTP delivery system
Handles sending OTP codes to voter email addresses for 2FA authentication
"""

import smtplib
import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
import json
import os
from config import Config
from utils.simple_otp_storage import otp_storage

class EmailService:
    def __init__(self):
        # Email configuration - using Gmail SMTP
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.email_address = Config.SMTP_EMAIL
        self.email_password = Config.SMTP_PASSWORD
        
        # OTP storage - using simple in-memory storage
        
    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP code"""
        digits = string.digits
        return ''.join(secrets.choice(digits) for _ in range(length))
    
    def send_otp_email(self, email: str, username: str) -> Dict[str, any]:
        """Send OTP to voter's email address"""
        try:
            # Generate OTP
            otp_code = self.generate_otp()
            
            # Store OTP with expiration (5 minutes) in memory
            expiry_time = datetime.now(timezone(timedelta(hours=5, minutes=30))) + timedelta(minutes=5)
            otp_data = {
                "otp": otp_code,
                "username": username,
                "expires_at": expiry_time.isoformat(),
                "attempts": 0
            }
            
            # Store in memory storage
            if not otp_storage.store_otp(email, otp_data):
                return {
                    "success": False,
                    "error": "Failed to store OTP. Please try again."
                }
            
            # Create email content
            subject = "SecureVote Pro - Your Login Verification Code"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                    .header {{ background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 30px; text-align: center; }}
                    .content {{ padding: 30px; }}
                    .otp-box {{ background: #f8f9fa; border: 2px dashed #2563eb; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }}
                    .otp-code {{ font-size: 32px; font-weight: bold; color: #2563eb; letter-spacing: 8px; font-family: monospace; }}
                    .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0; color: #856404; }}
                    .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🛡️ SecureVote Pro</h1>
                        <p>Two-Factor Authentication</p>
                    </div>
                    <div class="content">
                        <h2>Hello {username},</h2>
                        <p>You are attempting to log in to SecureVote Pro. To complete your login, please use the verification code below:</p>
                        
                        <div class="otp-box">
                            <div class="otp-code">{otp_code}</div>
                            <p style="margin: 10px 0 0 0; color: #666;">Enter this code in the login form</p>
                        </div>
                        
                        <div class="warning">
                            <strong>⚠️ Security Notice:</strong>
                            <ul style="margin: 10px 0; padding-left: 20px;">
                                <li>This code expires in <strong>5 minutes</strong></li>
                                <li>Never share this code with anyone</li>
                                <li>SecureVote Pro will never ask for this code via phone or email</li>
                                <li>If you didn't request this code, please ignore this email</li>
                            </ul>
                        </div>
                        
                        <p>If you're having trouble logging in, please contact your election administrator.</p>
                        
                        <p>Best regards,<br>
                        <strong>SecureVote Pro Security Team</strong></p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message from SecureVote Pro Election System</p>
                        <p>Generated at: {datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%Y-%m-%d %H:%M:%S IST')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_address
            msg['To'] = email
            
            # Add HTML content
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email (in development, we'll simulate this)
            if Config.DEVELOPMENT_MODE:
                # Development mode - just log the OTP
                print(f"🔐 [DEV MODE] OTP for {email}: {otp_code}")
                return {
                    "success": True,
                    "message": f"OTP sent to {email}",
                    "dev_otp": otp_code,  # Only in development
                    "expires_in": 300  # 5 minutes
                }
            else:
                # Production mode - actually send email
                if not self.email_address or not self.email_password:
                    return {
                        "success": False,
                        "error": "SMTP credentials not configured. Set SMTP_EMAIL and SMTP_PASSWORD."
                    }
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.email_address, self.email_password)
                    server.send_message(msg)
                
                return {
                    "success": True,
                    "message": f"OTP sent to {email}",
                    "expires_in": 300  # 5 minutes
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send OTP: {str(e)}"
            }
    
    def verify_otp(self, email: str, otp_code: str) -> Dict[str, any]:
        """Verify OTP code for email"""
        try:
            # Get OTP data from Redis storage
            stored_data = otp_storage.get_otp(email)
            
            if not stored_data:
                return {
                    "success": False,
                    "error": "No OTP found for this email. Please request a new one."
                }
            
            # Check if OTP has expired (Redis handles this automatically, but double-check)
            expiry_time = datetime.fromisoformat(stored_data["expires_at"])
            current_time = datetime.now(timezone(timedelta(hours=5, minutes=30)))
            
            if current_time > expiry_time:
                otp_storage.delete_otp(email)
                return {
                    "success": False,
                    "error": "OTP has expired. Please request a new one."
                }
            
            # Check attempt limit
            if stored_data["attempts"] >= 3:
                otp_storage.delete_otp(email)
                return {
                    "success": False,
                    "error": "Too many failed attempts. Please request a new OTP."
                }
            
            # Verify OTP
            if stored_data["otp"] == otp_code:
                username = stored_data["username"]
                otp_storage.delete_otp(email)  # Remove used OTP
                return {
                    "success": True,
                    "username": username,
                    "message": "OTP verified successfully"
                }
            else:
                # Increment failed attempts
                stored_data["attempts"] += 1
                otp_storage.update_otp(email, stored_data)
                remaining_attempts = 3 - stored_data["attempts"]
                return {
                    "success": False,
                    "error": f"Invalid OTP. {remaining_attempts} attempts remaining."
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"OTP verification failed: {str(e)}"
            }
    
    def cleanup_expired_otps(self):
        """Clean up expired OTPs from storage (Redis handles this automatically)"""
        return otp_storage.cleanup_expired_otps()

# Global email service instance
email_service = EmailService()
