#!/usr/bin/env python3
"""
Database clearing utility for SecureVote Pro
Clears all tables and resets the database to a fresh state
"""

import os
import sys
from sqlalchemy import create_engine, text
from database import Base, engine, SessionLocal
from config import Config

def clear_database():
    """Clear all data from the database tables"""
    print("🗑️  Clearing SecureVote Pro database...")
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Drop all tables
        print("   Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        
        # Recreate all tables
        print("   Recreating tables...")
        Base.metadata.create_all(bind=engine)
        
        # Commit the changes
        db.commit()
        print("✅ Database cleared successfully!")
        print("   All tables have been reset to empty state")
        
    except Exception as e:
        print(f"❌ Error clearing database: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

def clear_redis_cache():
    """Clear Redis cache if available"""
    try:
        from database import redis_client
        if hasattr(redis_client, 'data'):  # MockRedis
            redis_client.data.clear()
            print("✅ Mock Redis cache cleared")
        else:
            # Real Redis - clear all keys
            redis_client.flushall()
            print("✅ Redis cache cleared")
    except Exception as e:
        print(f"⚠️  Redis cache clear failed (this is okay): {str(e)}")

if __name__ == "__main__":
    print("=" * 50)
    print("SecureVote Pro - Database Reset Utility")
    print("=" * 50)
    
    # Confirm with user
    confirm = input("Are you sure you want to clear ALL database data? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Database clear cancelled")
        sys.exit(0)
    
    # Clear database
    if clear_database():
        # Clear Redis cache
        clear_redis_cache()
        
        print("\n🎉 Database reset complete!")
        print("   You can now start fresh with voter registration and testing")
    else:
        print("\n❌ Database reset failed!")
        sys.exit(1)
