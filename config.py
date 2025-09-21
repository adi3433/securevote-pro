import os
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, skip loading .env file
    pass

class Config:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./voting_system.db")
    
    # Redis (removed - using in-memory OTP storage)
    # REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    SALT = os.getenv("VOTER_SALT", "voting-system-salt-2024")
    
    # Demo mode
    DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
    
    # Environment mode
    DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "true").lower() == "true"
    
    # SMTP settings (used in production mode for sending OTP emails)
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    
    # Bloom filter settings
    BLOOM_FILTER_SIZE = int(os.getenv("BLOOM_FILTER_SIZE", "100000"))
    BLOOM_FILTER_HASH_COUNT = int(os.getenv("BLOOM_FILTER_HASH_COUNT", "7"))
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
