from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
import secrets
import json
from datetime import datetime, timezone, timedelta

from database import Voter, Ballot, Tally, AuditEvent, MerkleLeaf, OTACMapping, redis_client
from data_structures.bloom_filter import BloomFilter
from data_structures.merkle_tree import MerkleTree
from data_structures.audit_stack import AuditStack
from utils.crypto_utils import CryptoUtils
from config import Config

class VotingService:
    """Core voting service implementing the main business logic."""
    
    def __init__(self):
        self.bloom_filter = BloomFilter(Config.BLOOM_FILTER_SIZE, 0.01)
        self.audit_stack = AuditStack()
        self.merkle_tree = MerkleTree()
        self._load_existing_data()
    
    def _load_existing_data(self):
        """Load existing data into memory structures on startup."""
        # This would typically load from database/Redis on service restart
        pass
    
    def register_voters(self, db: Session, voter_ids: List[str]) -> Dict[str, any]:
        """
        Register voters by storing salted hashes of their IDs.
        
        Args:
            db: Database session
            voter_ids: List of original voter IDs
            
        Returns:
            Registration result with statistics
        """
        registered_count = 0
        duplicate_count = 0
        
        for voter_id in voter_ids:
            voter_hash = CryptoUtils.hash_voter_id(voter_id)
            print(f"DEBUG: Registering voter_id: {voter_id} -> hash: {voter_hash[:10]}...")
            
            # Check if already registered
            existing = db.query(Voter).filter(Voter.voter_id_hash == voter_hash).first()
            if existing:
                duplicate_count += 1
                continue
            
            # Add to database
            voter = Voter(voter_id_hash=voter_hash)
            db.add(voter)
            
            # Add to bloom filter for fast duplicate checking
            self.bloom_filter.add(voter_hash)
            
            # Cache in Redis
            redis_client.hset(f"voter:{voter_hash}", "hasVoted", "false")
            
            registered_count += 1
        
        db.commit()
        
        # Log audit event
        event = {
            "type": "REGISTER_VOTERS",
            "details": {
                "registered_count": registered_count,
                "duplicate_count": duplicate_count,
                "total_attempted": len(voter_ids)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        self.audit_stack.push(event)
        
        # Persist audit event
        audit_event = AuditEvent(
            type="REGISTER_VOTERS",
            details=json.dumps(event["details"])
        )
        db.add(audit_event)
        db.commit()
        
        return {
            "success": True,
            "registered_count": registered_count,
            "duplicate_count": duplicate_count,
            "total_voters": db.query(Voter).count()
        }
    
    def issue_otacs(self, db: Session, voter_ids: List[str]) -> Dict[str, any]:
        """
        Issue one-time access codes for registered voters.
        
        Args:
            db: Database session
            voter_ids: List of voter IDs to issue OTACs for
            
        Returns:
            Dictionary mapping voter IDs to OTACs
        """
        otacs = []
        issued_count = 0
        
        for voter_id in voter_ids:
            voter_hash = CryptoUtils.hash_voter_id(voter_id)
            print(f"DEBUG: Issuing OTAC for voter_id: {voter_id} -> hash: {voter_hash[:10]}...")
            
            # Check if voter is registered
            voter = db.query(Voter).filter(Voter.voter_id_hash == voter_hash).first()
            if not voter:
                print(f"DEBUG: Voter not found in database: {voter_id}")
                continue
            
            # Generate OTAC
            otac = CryptoUtils.generate_otac()
            otac_hash = CryptoUtils.hash_otac(otac)
            
            # Store mapping
            mapping = OTACMapping(
                otac_hash=otac_hash,
                voter_id_hash=voter_hash
            )
            db.add(mapping)
            
            otacs.append({"voter_id": voter_id, "otac": otac})
            issued_count += 1
        
        db.commit()
        
        # Log audit event
        event = {
            "type": "ISSUE_OTACS",
            "details": {
                "issued_count": issued_count,
                "requested_count": len(voter_ids)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        self.audit_stack.push(event)
        
        return {
            "success": True,
            "otacs": otacs,
            "issued_count": issued_count
        }
    
    def cast_vote(self, db: Session, otac: str, candidate_id: str) -> Dict[str, any]:
        """
        Cast a vote using OTAC.
        
        Args:
            db: Database session
            otac: One-time access code
            candidate_id: ID of selected candidate
            
        Returns:
            Vote casting result
        """
        try:
            # Hash OTAC for lookup
            otac_hash = CryptoUtils.hash_otac(otac)
            
            # Find OTAC mapping
            mapping = db.query(OTACMapping).filter(
                OTACMapping.otac_hash == otac_hash,
                OTACMapping.used == False
            ).first()
            
            if not mapping:
                return {"success": False, "error": "Invalid or used OTAC"}
            
            print(f"DEBUG: OTAC mapping found - voter_hash: {mapping.voter_id_hash[:10]}...")
            
            voter_hash = mapping.voter_id_hash
            
            # Fast duplicate check with Bloom filter (skip for now to debug)
            # if not self.bloom_filter.check(voter_hash):
            #     return {"success": False, "error": "Voter not eligible"}
            
            # Check voter eligibility and voting status
            voter = db.query(Voter).filter(Voter.voter_id_hash == voter_hash).first()
            if not voter:
                return {"success": False, "error": f"Voter not found. Hash: {voter_hash[:10]}..."}
            
            if voter.has_voted:
                return {"success": False, "error": "Voter has already voted"}
            
            # Database operations (SQLAlchemy handles transactions automatically)
            try:
                # Mark voter as voted
                voter.has_voted = True
                redis_client.hset(f"voter:{voter_hash}", "hasVoted", "true")
                
                # Mark OTAC as used
                mapping.used = True
                
                # Update tally
                tally = db.query(Tally).filter(Tally.candidate_id == candidate_id).first()
                if not tally:
                    tally = Tally(candidate_id=candidate_id, count=1)
                    db.add(tally)
                else:
                    tally.count += 1
                
                # Ensure tally is committed to database
                db.flush()
                
                # Generate ballot hash
                ballot_hash, nonce = CryptoUtils.generate_ballot_hash(candidate_id)
                
                # Get next sequence number
                max_seq = db.query(func.max(Ballot.seq)).scalar() or 0
                seq = max_seq + 1
                
                # Store ballot
                ballot = Ballot(
                    seq=seq,
                    ballot_hash=ballot_hash,
                    candidate_id=candidate_id
                )
                db.add(ballot)
                
                # Add to Merkle tree
                leaf = MerkleLeaf(seq=seq, ballot_hash=ballot_hash)
                db.add(leaf)
                
                # Update Merkle tree and get new root
                prev_root = self.merkle_tree.get_root()
                new_root = self.merkle_tree.add_leaf(ballot_hash)
                
                # Log audit event
                event = {
                    "type": "CAST",
                    "details": {
                        "voter_hash": voter_hash,
                        "ballot_hash": ballot_hash,
                        "candidate_id": candidate_id,
                        "seq": seq,
                        "nonce": nonce
                    },
                    "prev_root": prev_root,
                    "new_root": new_root,
                    "timestamp": datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat()
                }
                self.audit_stack.push(event)
                
                # Persist audit event
                audit_event = AuditEvent(
                    type="CAST",
                    details=json.dumps(event["details"]),
                    prev_root=prev_root,
                    new_root=new_root
                )
                db.add(audit_event)
                
                db.commit()
                
                return {
                    "success": True,
                    "ballot_hash": ballot_hash,
                    "seq": seq,
                    "new_root": new_root,
                    "timestamp": datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat(),
                    "message": "Vote cast successfully"
                }
                
            except Exception as e:
                db.rollback()
                return {"success": False, "error": f"Database error: {str(e)}"}
                
        except Exception as e:
            return {"success": False, "error": f"Failed to cast vote: {str(e)}"}
    
    def get_results(self, db: Session) -> Dict[str, any]:
        """Get current voting results."""
        tallies = db.query(Tally).all()
        
        results = []
        total_votes = 0
        
        for tally in tallies:
            results.append({
                "candidate_id": tally.candidate_id,
                "vote_count": tally.count
            })
            total_votes += tally.count
        
        return {
            "results": results,
            "total_votes": total_votes,
            "merkle_root": self.merkle_tree.get_root() if self.merkle_tree else "No votes cast yet"
        }
    
    def generate_merkle_proof(self, db: Session, ballot_hash: str) -> Dict[str, any]:
        """
        Generate Merkle inclusion proof for a ballot.
        
        Args:
            db: Database session
            ballot_hash: Hash of ballot to prove
            
        Returns:
            Proof data or error
        """
        # Find ballot
        ballot = db.query(Ballot).filter(Ballot.ballot_hash == ballot_hash).first()
        if not ballot:
            return {"success": False, "error": "Ballot not found"}
        
        try:
            # Generate proof
            leaf_index = ballot.seq - 1  # Convert to 0-based index
            proof = self.merkle_tree.get_proof(leaf_index)
            
            return {
                "success": True,
                "ballot_hash": ballot_hash,
                "leaf_index": leaf_index,
                "proof": proof,
                "root": self.merkle_tree.get_root(),
                "tree_size": self.merkle_tree.get_leaf_count()
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to generate proof: {str(e)}"}
    
    def verify_merkle_proof(self, leaf: str, leaf_index: int, proof: List[str], root: str) -> bool:
        """Verify Merkle inclusion proof."""
        return self.merkle_tree.verify_proof(leaf, leaf_index, proof, root)
    
    def undo_last_action(self, db: Session) -> Dict[str, any]:
        """
        Undo the last action (demo mode only).
        
        Args:
            db: Database session
            
        Returns:
            Undo result
        """
        if not Config.DEMO_MODE:
            return {"success": False, "error": "Undo only available in demo mode"}
        
        if self.audit_stack.is_empty():
            return {"success": False, "error": "No actions to undo"}
        
        event = self.audit_stack.pop()
        
        try:
            
            if event["type"] == "CAST":
                details = event["details"]
                voter_hash = details["voter_hash"]
                ballot_hash = details["ballot_hash"]
                candidate_id = details["candidate_id"]
                seq = details["seq"]
                
                # Restore voter status
                voter = db.query(Voter).filter(Voter.voter_id_hash == voter_hash).first()
                if voter:
                    voter.has_voted = False
                    redis_client.hset(f"voter:{voter_hash}", "hasVoted", "false")
                
                # Update tally
                tally = db.query(Tally).filter(Tally.candidate_id == candidate_id).first()
                if tally and tally.count > 0:
                    tally.count -= 1
                
                # Remove ballot
                db.query(Ballot).filter(Ballot.ballot_hash == ballot_hash).delete()
                db.query(MerkleLeaf).filter(MerkleLeaf.seq == seq).delete()
                
                # Rebuild Merkle tree
                remaining_leaves = db.query(MerkleLeaf).order_by(MerkleLeaf.seq).all()
                leaf_hashes = [leaf.ballot_hash for leaf in remaining_leaves]
                self.merkle_tree = MerkleTree(leaf_hashes)
                
                new_root = self.merkle_tree.get_root()
                
                # Log undo event
                undo_event = AuditEvent(
                    type="UNDO",
                    details=json.dumps({"undone_event": event}),
                    prev_root=event.get("new_root"),
                    new_root=new_root
                )
                db.add(undo_event)
                
                db.commit()
                
                return {
                    "success": True,
                    "undone_action": event["type"],
                    "new_root": new_root,
                    "message": "Action undone successfully"
                }
            
            else:
                db.rollback()
                return {"success": False, "error": f"Cannot undo action of type: {event['type']}"}
                
        except Exception as e:
            db.rollback()
            return {"success": False, "error": f"Failed to undo action: {str(e)}"}
    
    def get_audit_trail(self, db: Session, limit: int = 50) -> List[Dict]:
        """Get audit trail (without PII)."""
        events = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(limit).all()
        
        trail = []
        for event in events:
            # Parse JSON details
            try:
                details = json.loads(event.details) if event.details else {}
            except:
                details = {}
            
            # Remove PII from details
            sanitized_details = details.copy()
            if "voter_hash" in sanitized_details:
                sanitized_details["voter_hash"] = "***REDACTED***"
            
            trail.append({
                "id": event.id,
                "type": event.type,
                "details": sanitized_details,
                "prev_root": event.prev_root,
                "new_root": event.new_root,
                "timestamp": event.timestamp.isoformat()
            })
        
        return trail
    
    def lookup_ballot(self, db: Session, ballot_hash: str) -> Dict[str, any]:
        """Lookup ballot details by hash."""
        try:
            ballot = db.query(Ballot).filter(Ballot.ballot_hash == ballot_hash).first()
            
            if ballot:
                return {
                    "found": True,
                    "ballot": {
                        "seq": ballot.seq,
                        "ballot_hash": ballot.ballot_hash,
                        "candidate_id": ballot.candidate_id,
                        "timestamp": ballot.timestamp.isoformat()
                    }
                }
            else:
                return {
                    "found": False,
                    "error": "Ballot hash not found in the system"
                }
        except Exception as e:
            return {
                "found": False,
                "error": f"Database error: {str(e)}"
            }
    
    def get_system_stats(self, db: Session) -> Dict[str, any]:
        """Get system statistics."""
        total_voters = db.query(Voter).count()
        voted_count = db.query(Voter).filter(Voter.has_voted == True).count()
        total_ballots = db.query(Ballot).count()
        
        return {
            "total_voters": total_voters,
            "voted_count": voted_count,
            "remaining_voters": total_voters - voted_count,
            "total_ballots": total_ballots,
            "merkle_stats": self.merkle_tree.get_stats(),
            "bloom_filter_stats": self.bloom_filter.get_stats(),
            "audit_stack_stats": self.audit_stack.get_stats(),
            "demo_mode": Config.DEMO_MODE
        }
