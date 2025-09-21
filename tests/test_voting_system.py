import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import tempfile
import os

from database import Base, get_db
from main import app
from services.voting_service import VotingService
from data_structures.bloom_filter import BloomFilter
from data_structures.merkle_tree import MerkleTree
from data_structures.audit_stack import AuditStack
from utils.crypto_utils import CryptoUtils
from utils.lab_utils import LabUtils

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def voting_service():
    return VotingService()

class TestBloomFilter:
    """Test Bloom Filter implementation."""
    
    def test_bloom_filter_creation(self):
        bf = BloomFilter(1000, 0.01)
        assert bf.capacity == 1000
        assert bf.error_rate == 0.01
        assert bf.items_count == 0
    
    def test_bloom_filter_add_and_check(self):
        bf = BloomFilter(1000, 0.01)
        
        # Add items
        bf.add("test1")
        bf.add("test2")
        
        # Check items
        assert bf.check("test1") == True
        assert bf.check("test2") == True
        assert bf.check("test3") == False  # Might be false positive, but unlikely
    
    def test_bloom_filter_stats(self):
        bf = BloomFilter(1000, 0.01)
        bf.add("test")
        
        stats = bf.get_stats()
        assert stats["items_count"] == 1
        assert stats["capacity"] == 1000

class TestMerkleTree:
    """Test Merkle Tree implementation."""
    
    def test_empty_tree(self):
        tree = MerkleTree()
        assert tree.get_root() is None
        assert tree.get_leaf_count() == 0
    
    def test_single_leaf(self):
        tree = MerkleTree(["leaf1"])
        assert tree.get_root() is not None
        assert tree.get_leaf_count() == 1
    
    def test_multiple_leaves(self):
        leaves = ["leaf1", "leaf2", "leaf3", "leaf4"]
        tree = MerkleTree(leaves)
        
        assert tree.get_leaf_count() == 4
        assert tree.get_root() is not None
    
    def test_add_leaf(self):
        tree = MerkleTree(["leaf1"])
        initial_root = tree.get_root()
        
        new_root = tree.add_leaf("leaf2")
        assert new_root != initial_root
        assert tree.get_leaf_count() == 2
    
    def test_proof_generation_and_verification(self):
        leaves = ["leaf1", "leaf2", "leaf3", "leaf4"]
        tree = MerkleTree(leaves)
        
        # Generate proof for first leaf
        proof = tree.get_proof(0)
        root = tree.get_root()
        
        # Verify proof
        is_valid = tree.verify_proof("leaf1", 0, proof, root)
        assert is_valid == True
        
        # Test invalid proof
        is_invalid = tree.verify_proof("wrong_leaf", 0, proof, root)
        assert is_invalid == False
    
    def test_remove_leaf(self):
        leaves = ["leaf1", "leaf2", "leaf3"]
        tree = MerkleTree(leaves)
        initial_count = tree.get_leaf_count()
        
        new_root = tree.remove_leaf(1)  # Remove "leaf2"
        assert tree.get_leaf_count() == initial_count - 1
        assert new_root is not None

class TestAuditStack:
    """Test Audit Stack implementation."""
    
    def test_empty_stack(self):
        stack = AuditStack()
        assert stack.is_empty() == True
        assert stack.size() == 0
        assert stack.peek() is None
        assert stack.pop() is None
    
    def test_push_and_pop(self):
        stack = AuditStack()
        
        event = {"type": "TEST", "data": "test_data"}
        stack.push(event)
        
        assert stack.size() == 1
        assert stack.is_empty() == False
        
        popped = stack.pop()
        assert popped["type"] == "TEST"
        assert stack.is_empty() == True
    
    def test_peek(self):
        stack = AuditStack()
        
        event = {"type": "TEST", "data": "test_data"}
        stack.push(event)
        
        peeked = stack.peek()
        assert peeked["type"] == "TEST"
        assert stack.size() == 1  # Should not remove item
    
    def test_get_recent_events(self):
        stack = AuditStack()
        
        for i in range(5):
            stack.push({"type": "TEST", "id": i})
        
        recent = stack.get_recent_events(3)
        assert len(recent) == 3
        assert recent[-1]["id"] == 4  # Most recent

class TestCryptoUtils:
    """Test cryptographic utilities."""
    
    def test_hash_voter_id(self):
        voter_id = "voter123"
        hash1 = CryptoUtils.hash_voter_id(voter_id)
        hash2 = CryptoUtils.hash_voter_id(voter_id)
        
        # Same input should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length
    
    def test_generate_otac(self):
        otac1 = CryptoUtils.generate_otac()
        otac2 = CryptoUtils.generate_otac()
        
        # Should generate different OTACs
        assert otac1 != otac2
        assert len(otac1) > 0
    
    def test_ballot_hash_generation(self):
        candidate_id = "candidate_a"
        ballot_hash, nonce = CryptoUtils.generate_ballot_hash(candidate_id)
        
        assert len(ballot_hash) == 64  # SHA-256 hex length
        assert len(nonce) > 0
        
        # Verify hash
        is_valid = CryptoUtils.verify_ballot_hash(candidate_id, nonce, ballot_hash)
        assert is_valid == True

class TestLabUtils:
    """Test lab utility functions."""
    
    def test_manhattan_distance(self):
        p1 = (0, 0)
        p2 = (3, 4)
        
        distance = LabUtils.manhattan_distance(p1, p2)
        assert distance == 7  # |3-0| + |4-0| = 7
    
    def test_find_nearest_polling_station(self):
        voter_location = (5, 5)
        stations = [(0, 0, "station1"), (10, 10, "station2"), (6, 6, "station3")]
        
        nearest, distance = LabUtils.find_nearest_polling_station(voter_location, stations)
        assert nearest == "station3"
        assert distance == 2  # |6-5| + |6-5| = 2
    
    def test_collinear_points(self):
        # Collinear points
        p1, p2, p3 = (0, 0), (1, 1), (2, 2)
        assert LabUtils.are_collinear(p1, p2, p3) == True
        
        # Non-collinear points
        p1, p2, p3 = (0, 0), (1, 1), (2, 0)
        assert LabUtils.are_collinear(p1, p2, p3) == False
    
    def test_triangular_number(self):
        assert LabUtils.triangular_number(1) == 1
        assert LabUtils.triangular_number(3) == 6
        assert LabUtils.triangular_number(5) == 15
    
    def test_pair_indexing(self):
        # Test pair to index conversion
        index = LabUtils.pair_to_index(1, 3, 5)
        i, j = LabUtils.index_to_pair(index, 5)
        
        assert i == 1
        assert j == 3

class TestVotingSystem:
    """Integration tests for the voting system."""
    
    def test_register_voters_endpoint(self, client, setup_database):
        # Create test CSV content
        csv_content = "voter1\nvoter2\nvoter3"
        
        response = client.post(
            "/api/registerVoters",
            files={"file": ("voters.csv", csv_content, "text/csv")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["registered_count"] == 3
    
    def test_issue_otacs_endpoint(self, client, setup_database):
        # First register voters
        csv_content = "voter1\nvoter2"
        client.post(
            "/api/registerVoters",
            files={"file": ("voters.csv", csv_content, "text/csv")}
        )
        
        # Issue OTACs
        response = client.post(
            "/api/issueOtacs",
            json=["voter1", "voter2"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["issued_count"] == 2
        assert "otac_mappings" in data
    
    def test_cast_vote_endpoint(self, client, setup_database):
        # Register voter and issue OTAC
        csv_content = "voter1"
        client.post(
            "/api/registerVoters",
            files={"file": ("voters.csv", csv_content, "text/csv")}
        )
        
        otac_response = client.post("/api/issueOtacs", json=["voter1"])
        otac = otac_response.json()["otac_mappings"]["voter1"]
        
        # Cast vote
        response = client.post(
            "/api/castVote",
            json={"otac": otac, "candidate_id": "candidate_a"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "ballot_hash" in data
    
    def test_get_results_endpoint(self, client, setup_database):
        response = client.get("/api/results")
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total_votes" in data
    
    def test_merkle_proof_endpoint(self, client, setup_database):
        # First cast a vote to have a ballot
        csv_content = "voter1"
        client.post(
            "/api/registerVoters",
            files={"file": ("voters.csv", csv_content, "text/csv")}
        )
        
        otac_response = client.post("/api/issueOtacs", json=["voter1"])
        otac = otac_response.json()["otac_mappings"]["voter1"]
        
        vote_response = client.post(
            "/api/castVote",
            json={"otac": otac, "candidate_id": "candidate_a"}
        )
        ballot_hash = vote_response.json()["ballot_hash"]
        
        # Get proof
        response = client.post(
            "/api/proof",
            json={"ballot_hash": ballot_hash}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "proof" in data
    
    def test_audit_trail_endpoint(self, client, setup_database):
        response = client.get("/api/auditTrail")
        
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
    
    def test_system_stats_endpoint(self, client, setup_database):
        response = client.get("/api/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_voters" in data
        assert "merkle_stats" in data

class TestPerformance:
    """Performance and complexity tests."""
    
    def test_merkle_tree_performance(self):
        import time
        
        sizes = [100, 500, 1000]
        times = []
        
        for size in sizes:
            leaves = [f"leaf_{i}" for i in range(size)]
            
            start_time = time.time()
            tree = MerkleTree(leaves)
            tree.get_proof(0)  # Generate proof for first leaf
            end_time = time.time()
            
            times.append(end_time - start_time)
        
        # Generate performance report
        perf_data = LabUtils.generate_performance_data("Merkle Tree", sizes, times)
        
        assert perf_data["algorithm"] == "Merkle Tree"
        assert len(perf_data["data_points"]) == 3
    
    def test_bloom_filter_performance(self):
        import time
        
        bf = BloomFilter(10000, 0.01)
        
        # Test insertion performance
        start_time = time.time()
        for i in range(1000):
            bf.add(f"item_{i}")
        insertion_time = time.time() - start_time
        
        # Test lookup performance
        start_time = time.time()
        for i in range(1000):
            bf.check(f"item_{i}")
        lookup_time = time.time() - start_time
        
        assert insertion_time < 1.0  # Should be very fast
        assert lookup_time < 0.1    # Lookups should be even faster

if __name__ == "__main__":
    pytest.main([__file__])
