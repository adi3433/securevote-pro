import math
from typing import List, Tuple, Optional

class LabUtils:
    """
    Utilities that reuse algorithms from DS course labs.
    Demonstrates integration of taught concepts into the voting system.
    """
    
    @staticmethod
    def manhattan_distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> int:
        """
        Calculate Manhattan distance between two points.
        Used for polling station assignment in demo.
        
        Args:
            point1: First point (x, y)
            point2: Second point (x, y)
            
        Returns:
            Manhattan distance
        """
        return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])
    
    @staticmethod
    def find_nearest_polling_station(voter_location: Tuple[int, int], 
                                   stations: List[Tuple[int, int, str]]) -> Optional[Tuple[str, int]]:
        """
        Find nearest polling station using Manhattan distance.
        
        Args:
            voter_location: Voter's (x, y) coordinates
            stations: List of (x, y, station_id) tuples
            
        Returns:
            Tuple of (station_id, distance) or None if no stations
        """
        if not stations:
            return None
        
        min_distance = float('inf')
        nearest_station = None
        
        for x, y, station_id in stations:
            distance = LabUtils.manhattan_distance(voter_location, (x, y))
            if distance < min_distance:
                min_distance = distance
                nearest_station = station_id
        
        return (nearest_station, min_distance)
    
    @staticmethod
    def are_collinear(p1: Tuple[int, int], p2: Tuple[int, int], p3: Tuple[int, int]) -> bool:
        """
        Check if three points are collinear.
        Used for route visualization and map plotting.
        
        Args:
            p1, p2, p3: Points as (x, y) tuples
            
        Returns:
            True if points are collinear
        """
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        
        # Using cross product: (p2-p1) × (p3-p1) = 0 for collinear points
        cross_product = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
        return cross_product == 0
    
    @staticmethod
    def triangular_number(n: int) -> int:
        """
        Calculate nth triangular number.
        Used for compact pair indexing in audit comparisons.
        
        Args:
            n: Position in sequence
            
        Returns:
            nth triangular number
        """
        return n * (n + 1) // 2
    
    @staticmethod
    def pair_to_index(i: int, j: int, n: int) -> int:
        """
        Map pair (i,j) to single index using triangular numbers.
        Useful for storing upper triangle of pairwise comparisons.
        
        Args:
            i, j: Pair indices (i < j)
            n: Total number of elements
            
        Returns:
            Single index for the pair
        """
        if i >= j:
            raise ValueError("i must be less than j")
        
        # Use triangular number formula for upper triangle mapping
        return LabUtils.triangular_number(i) + (j - i - 1)
    
    @staticmethod
    def index_to_pair(index: int, n: int) -> Tuple[int, int]:
        """
        Convert single index back to pair (i,j).
        
        Args:
            index: Single index
            n: Total number of elements
            
        Returns:
            Tuple (i, j) where i < j
        """
        # Find i using inverse triangular number
        i = 0
        while LabUtils.triangular_number(i + 1) <= index:
            i += 1
        
        j = index - LabUtils.triangular_number(i) + i + 1
        return (i, j)
    
    @staticmethod
    def circumcenter(p1: Tuple[float, float], p2: Tuple[float, float], 
                    p3: Tuple[float, float]) -> Optional[Tuple[float, float]]:
        """
        Calculate circumcenter of triangle formed by three points.
        Used for visualization and geometric demos.
        
        Args:
            p1, p2, p3: Triangle vertices as (x, y) tuples
            
        Returns:
            Circumcenter coordinates or None if points are collinear
        """
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        
        # Check if points are collinear
        if LabUtils.are_collinear(p1, p2, p3):
            return None
        
        # Calculate circumcenter using determinant formula
        d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        
        if abs(d) < 1e-10:  # Avoid division by zero
            return None
        
        ux = ((x1*x1 + y1*y1) * (y2 - y3) + 
              (x2*x2 + y2*y2) * (y3 - y1) + 
              (x3*x3 + y3*y3) * (y1 - y2)) / d
        
        uy = ((x1*x1 + y1*y1) * (x3 - x2) + 
              (x2*x2 + y2*y2) * (x1 - x3) + 
              (x3*x3 + y3*y3) * (x2 - x1)) / d
        
        return (ux, uy)
    
    @staticmethod
    def brute_force_closest_pair(points: List[Tuple[float, float]]) -> Tuple[float, Tuple[int, int]]:
        """
        Brute force algorithm to find closest pair of points.
        Used for performance comparison experiments (O(n²) vs optimized algorithms).
        
        Args:
            points: List of (x, y) coordinate tuples
            
        Returns:
            Tuple of (min_distance, (index1, index2))
        """
        if len(points) < 2:
            return float('inf'), (-1, -1)
        
        min_distance = float('inf')
        closest_pair = (-1, -1)
        
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                x1, y1 = points[i]
                x2, y2 = points[j]
                distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_pair = (i, j)
        
        return min_distance, closest_pair
    
    @staticmethod
    def generate_performance_data(algorithm_name: str, sizes: List[int], 
                                times: List[float]) -> dict:
        """
        Generate performance analysis data for algorithms.
        Used in evaluation reports and complexity demonstrations.
        
        Args:
            algorithm_name: Name of the algorithm
            sizes: List of input sizes
            times: List of corresponding execution times
            
        Returns:
            Dictionary with performance metrics
        """
        if len(sizes) != len(times):
            raise ValueError("Sizes and times lists must have same length")
        
        # Calculate growth rate (approximate)
        growth_rates = []
        for i in range(1, len(sizes)):
            if times[i-1] > 0:
                rate = times[i] / times[i-1]
                growth_rates.append(rate)
        
        avg_growth_rate = sum(growth_rates) / len(growth_rates) if growth_rates else 0
        
        return {
            "algorithm": algorithm_name,
            "data_points": list(zip(sizes, times)),
            "min_time": min(times) if times else 0,
            "max_time": max(times) if times else 0,
            "avg_growth_rate": avg_growth_rate,
            "complexity_estimate": LabUtils._estimate_complexity(sizes, times)
        }
    
    @staticmethod
    def _estimate_complexity(sizes: List[int], times: List[float]) -> str:
        """Estimate algorithmic complexity based on growth pattern."""
        if len(sizes) < 2:
            return "insufficient_data"
        
        # Simple heuristic based on growth rate
        ratios = []
        for i in range(1, len(sizes)):
            if times[i-1] > 0 and sizes[i-1] > 0:
                time_ratio = times[i] / times[i-1]
                size_ratio = sizes[i] / sizes[i-1]
                ratios.append(time_ratio / size_ratio)
        
        if not ratios:
            return "unknown"
        
        avg_ratio = sum(ratios) / len(ratios)
        
        if avg_ratio < 1.5:
            return "O(n)"
        elif avg_ratio < 3:
            return "O(n log n)"
        elif avg_ratio < 5:
            return "O(n²)"
        else:
            return "O(n³) or higher"
