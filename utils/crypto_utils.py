import hashlib
import secrets
import hmac
from typing import Tuple
from config import Config

class CryptoUtils:
    """Cryptographic utilities for the voting system."""
    
    @staticmethod
    def hash_voter_id(voter_id: str) -> str:
        """
        Create salted hash of voter ID.
        
        Args:
            voter_id: Original voter ID
            
        Returns:
            Salted hash of voter ID
        """
        combined = Config.SALT + voter_id
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def hash_otac(otac: str) -> str:
        """
        Hash OTAC for secure storage.
        
        Args:
            otac: One-time access code
            
        Returns:
            Hash of OTAC
        """
        return hashlib.sha256(otac.encode()).hexdigest()
    
    @staticmethod
    def generate_otac() -> str:
        """
        Generate secure one-time access code.
        
        Returns:
            Random OTAC string
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_ballot_hash(candidate_id: str, round_salt: str = None) -> Tuple[str, str]:
        """
        Generate ballot hash with nonce for anonymity.
        
        Args:
            candidate_id: ID of selected candidate
            round_salt: Optional round-specific salt
            
        Returns:
            Tuple of (ballot_hash, nonce)
        """
        if round_salt is None:
            round_salt = Config.SALT
        
        nonce = secrets.token_hex(16)
        combined = round_salt + candidate_id + nonce
        ballot_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        return ballot_hash, nonce
    
    @staticmethod
    def verify_ballot_hash(candidate_id: str, nonce: str, ballot_hash: str, round_salt: str = None) -> bool:
        """
        Verify ballot hash integrity.
        
        Args:
            candidate_id: ID of candidate
            nonce: Nonce used in hash generation
            ballot_hash: Hash to verify
            round_salt: Round-specific salt
            
        Returns:
            True if hash is valid
        """
        if round_salt is None:
            round_salt = Config.SALT
        
        combined = round_salt + candidate_id + nonce
        expected_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        return hmac.compare_digest(expected_hash, ballot_hash)
    
    @staticmethod
    def secure_random_int(max_value: int) -> int:
        """
        Generate cryptographically secure random integer.
        
        Args:
            max_value: Maximum value (exclusive)
            
        Returns:
            Random integer between 0 and max_value-1
        """
        return secrets.randbelow(max_value)
