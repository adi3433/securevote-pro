"""
Simple In-Memory OTP Storage for SecureVote Pro
Lightweight OTP storage without external dependencies
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

class SimpleOTPStorage:
    """Simple in-memory OTP storage with automatic cleanup"""
    
    def __init__(self):
        self.storage = {}  # email -> otp_data
        print("✅ Using in-memory OTP storage")
    
    def store_otp(self, email: str, otp_data: Dict) -> bool:
        """
        Store OTP data in memory
        
        Args:
            email: User's email address
            otp_data: Dict containing otp, username, expires_at, attempts
            
        Returns:
            bool: True if stored successfully
        """
        try:
            self.storage[email] = otp_data
            return True
        except Exception as e:
            print(f"❌ Failed to store OTP: {e}")
            return False
    
    def get_otp(self, email: str) -> Optional[Dict]:
        """
        Retrieve OTP data for email
        
        Args:
            email: User's email address
            
        Returns:
            Dict or None: OTP data if found and not expired
        """
        try:
            otp_data = self.storage.get(email)
            
            if otp_data:
                # Check if expired
                expires_at = datetime.fromisoformat(otp_data["expires_at"])
                current_time = datetime.now(timezone(timedelta(hours=5, minutes=30)))
                
                if current_time > expires_at:
                    # Remove expired OTP
                    del self.storage[email]
                    return None
                
                return otp_data
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to get OTP: {e}")
            return None
    
    def update_otp(self, email: str, otp_data: Dict) -> bool:
        """
        Update OTP data (e.g., increment attempts)
        
        Args:
            email: User's email address
            otp_data: Updated OTP data
            
        Returns:
            bool: True if updated successfully
        """
        return self.store_otp(email, otp_data)
    
    def delete_otp(self, email: str) -> bool:
        """
        Delete OTP data for email
        
        Args:
            email: User's email address
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            if email in self.storage:
                del self.storage[email]
            return True
        except Exception as e:
            print(f"❌ Failed to delete OTP: {e}")
            return True
    
    def cleanup_expired_otps(self) -> int:
        """
        Clean up expired OTPs
        
        Returns:
            int: Number of expired OTPs cleaned up
        """
        current_time = datetime.now(timezone(timedelta(hours=5, minutes=30)))
        expired_emails = []
        
        for email, data in self.storage.items():
            try:
                expires_at = datetime.fromisoformat(data["expires_at"])
                if current_time > expires_at:
                    expired_emails.append(email)
            except:
                # Invalid data, mark for deletion
                expired_emails.append(email)
        
        for email in expired_emails:
            del self.storage[email]
        
        return len(expired_emails)
    
    def get_stats(self) -> Dict:
        """
        Get storage statistics
        
        Returns:
            Dict: Storage statistics
        """
        return {
            "storage_type": "memory",
            "active_otps": len(self.storage),
            "redis_connected": False
        }

# Global OTP storage instance
otp_storage = SimpleOTPStorage()
