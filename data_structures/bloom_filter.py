import mmh3
from bitarray import bitarray
import math
from typing import Union

class BloomFilter:
    """
    Bloom filter implementation for fast duplicate checking.
    Used for pre-checking OTAC/voter hash duplicates before DB lookup.
    """
    
    def __init__(self, capacity: int, error_rate: float = 0.01):
        """
        Initialize Bloom filter with given capacity and error rate.
        
        Args:
            capacity: Expected number of elements
            error_rate: Desired false positive rate
        """
        self.capacity = capacity
        self.error_rate = error_rate
        
        # Calculate optimal bit array size and hash function count
        self.bit_array_size = self._get_size(capacity, error_rate)
        self.hash_count = self._get_hash_count(self.bit_array_size, capacity)
        
        # Initialize bit array
        self.bit_array = bitarray(self.bit_array_size)
        self.bit_array.setall(0)
        
        self.items_count = 0
    
    def _get_size(self, n: int, p: float) -> int:
        """
        Calculate optimal bit array size.
        Formula: m = -(n * ln(p)) / (ln(2)^2)
        """
        m = -(n * math.log(p)) / (math.log(2) ** 2)
        return int(m)
    
    def _get_hash_count(self, m: int, n: int) -> int:
        """
        Calculate optimal number of hash functions.
        Formula: k = (m/n) * ln(2)
        """
        k = (m / n) * math.log(2)
        return int(k)
    
    def _hash(self, item: str, seed: int) -> int:
        """Generate hash for given item with seed."""
        return mmh3.hash(item, seed) % self.bit_array_size
    
    def add(self, item: str) -> None:
        """Add item to bloom filter."""
        for i in range(self.hash_count):
            index = self._hash(item, i)
            self.bit_array[index] = 1
        self.items_count += 1
    
    def check(self, item: str) -> bool:
        """
        Check if item might be in the set.
        Returns True if item might be present (could be false positive).
        Returns False if item is definitely not present.
        """
        for i in range(self.hash_count):
            index = self._hash(item, i)
            if self.bit_array[index] == 0:
                return False
        return True
    
    def get_stats(self) -> dict:
        """Get bloom filter statistics."""
        return {
            "capacity": self.capacity,
            "items_count": self.items_count,
            "bit_array_size": self.bit_array_size,
            "hash_count": self.hash_count,
            "error_rate": self.error_rate,
            "current_error_rate": self._current_error_rate()
        }
    
    def _current_error_rate(self) -> float:
        """Calculate current false positive rate."""
        if self.items_count == 0:
            return 0.0
        return (1 - math.exp(-self.hash_count * self.items_count / self.bit_array_size)) ** self.hash_count
