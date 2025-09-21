import hashlib
from typing import List, Optional, Tuple
import math

class MerkleTree:
    """
    Merkle Tree implementation for tamper-evident ballot logging.
    Provides O(log n) inclusion proofs and tamper detection.
    """
    
    def __init__(self, leaves: List[str] = None):
        """Initialize Merkle tree with optional initial leaves."""
        self.leaves = leaves or []
        self.tree = []
        self.root = None
        if self.leaves:
            self._build_tree()
    
    def _hash(self, data: str) -> str:
        """Generate SHA-256 hash of data."""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _build_tree(self) -> None:
        """Build the complete Merkle tree from leaves."""
        if not self.leaves:
            self.root = None
            return
        
        # Start with leaf hashes
        current_level = [self._hash(leaf) for leaf in self.leaves]
        self.tree = [current_level[:]]  # Store each level
        
        # Build tree bottom-up
        while len(current_level) > 1:
            next_level = []
            
            # Process pairs
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                
                # Combine hashes
                combined = left + right
                parent_hash = self._hash(combined)
                next_level.append(parent_hash)
            
            self.tree.append(next_level[:])
            current_level = next_level
        
        self.root = current_level[0] if current_level else None
    
    def add_leaf(self, leaf: str) -> str:
        """
        Add a new leaf and rebuild tree.
        Returns new root hash.
        """
        self.leaves.append(leaf)
        self._build_tree()
        return self.root
    
    def get_root(self) -> Optional[str]:
        """Get current root hash."""
        return self.root
    
    def get_proof(self, leaf_index: int) -> List[str]:
        """
        Generate inclusion proof for leaf at given index.
        Returns list of sibling hashes needed to reconstruct root.
        """
        if leaf_index >= len(self.leaves) or leaf_index < 0:
            raise ValueError("Invalid leaf index")
        
        if not self.tree:
            return []
        
        proof = []
        current_index = leaf_index
        
        # Traverse from leaf to root, collecting sibling hashes
        for level in range(len(self.tree) - 1):
            level_nodes = self.tree[level]
            
            # Find sibling index
            if current_index % 2 == 0:  # Left child
                sibling_index = current_index + 1
            else:  # Right child
                sibling_index = current_index - 1
            
            # Add sibling hash if it exists
            if sibling_index < len(level_nodes):
                proof.append(level_nodes[sibling_index])
            else:
                # No sibling (odd number of nodes), use same node
                proof.append(level_nodes[current_index])
            
            # Move to parent index
            current_index = current_index // 2
        
        return proof
    
    def verify_proof(self, leaf: str, leaf_index: int, proof: List[str], root: str) -> bool:
        """
        Verify inclusion proof for a leaf.
        
        Args:
            leaf: Original leaf data
            leaf_index: Index of leaf in tree
            proof: List of sibling hashes
            root: Expected root hash
        
        Returns:
            True if proof is valid, False otherwise
        """
        if leaf_index >= len(self.leaves):
            return False
        
        # Start with leaf hash
        current_hash = self._hash(leaf)
        current_index = leaf_index
        
        # Reconstruct path to root
        for sibling_hash in proof:
            if current_index % 2 == 0:  # Left child
                combined = current_hash + sibling_hash
            else:  # Right child
                combined = sibling_hash + current_hash
            
            current_hash = self._hash(combined)
            current_index = current_index // 2
        
        return current_hash == root
    
    def get_leaf_count(self) -> int:
        """Get number of leaves in tree."""
        return len(self.leaves)
    
    def get_tree_height(self) -> int:
        """Get height of tree."""
        if not self.leaves:
            return 0
        return math.ceil(math.log2(len(self.leaves))) + 1
    
    def remove_leaf(self, leaf_index: int) -> Optional[str]:
        """
        Remove leaf at index and rebuild tree.
        Used for undo operations in demo mode.
        Returns new root hash or None if tree becomes empty.
        """
        if leaf_index >= len(self.leaves) or leaf_index < 0:
            raise ValueError("Invalid leaf index")
        
        self.leaves.pop(leaf_index)
        if self.leaves:
            self._build_tree()
            return self.root
        else:
            self.root = None
            self.tree = []
            return None
    
    def get_stats(self) -> dict:
        """Get tree statistics."""
        return {
            "leaf_count": len(self.leaves),
            "tree_height": self.get_tree_height(),
            "root_hash": self.root,
            "proof_size_bytes": len(self.get_proof(0)) * 64 if self.leaves else 0  # SHA-256 = 64 hex chars
        }
