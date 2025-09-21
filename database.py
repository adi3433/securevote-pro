from sqlalchemy import create_engine, Column, String, Boolean, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from config import Config

try:
    import redis
except ImportError:
    redis = None

Base = declarative_base()

class Voter(Base):
    __tablename__ = "voters"
    
    voter_id_hash = Column(String, primary_key=True)
    has_voted = Column(Boolean, default=False)

class Ballot(Base):
    __tablename__ = "ballots"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    seq = Column(Integer, unique=True, nullable=False)
    ballot_hash = Column(String, unique=True, nullable=False)
    candidate_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())

class Tally(Base):
    __tablename__ = "tally"
    
    candidate_id = Column(String, primary_key=True)
    count = Column(Integer, nullable=False, default=0)

class AuditEvent(Base):
    __tablename__ = "audit"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    details = Column(String)
    prev_root = Column(String)
    new_root = Column(String)
    timestamp = Column(DateTime, default=func.now())

class MerkleLeaf(Base):
    __tablename__ = "leaves"
    
    seq = Column(Integer, primary_key=True)
    ballot_hash = Column(String, nullable=False)

class OTACMapping(Base):
    __tablename__ = "otac_mappings"
    
    otac_hash = Column(String, primary_key=True)
    voter_id_hash = Column(String, nullable=False)
    used = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=func.now())

# Database setup
engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis setup (optional - will use in-memory fallback if Redis not available)
if redis:
    try:
        redis_client = redis.from_url(Config.REDIS_URL)
        redis_client.ping()  # Test connection
    except:
        redis_client = None
else:
    redis_client = None

# Fallback to mock Redis for development if Redis is not available
if redis_client is None:
    class MockRedis:
        def __init__(self):
            self.data = {}
        def hset(self, key, field, value):
            if key not in self.data:
                self.data[key] = {}
            self.data[key][field] = value
        def hget(self, key, field):
            return self.data.get(key, {}).get(field)
        def ping(self):
            return True
    redis_client = MockRedis()

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
