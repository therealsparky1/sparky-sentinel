"""
Test suite for side-channel mitigation library.
Verifies correctness and resistance to timing/power/cache attacks.
"""

import unittest
import time
import statistics
from side_channel_mitigations import (
    TimingAttackPrevention,
    PowerAnalysisDefense,
    CacheTimingDefense,
    SideChannelBenchmark
)


class TestTimingAttackPrevention(unittest.TestCase):
    """Test constant-time operations."""
    
    def test_constant_time_compare_equal(self):
        """Test constant-time comparison with equal inputs."""
        a = b"secret_key_12345"
        b = b"secret_key_12345"
        self.assertTrue(TimingAttackPrevention.constant_time_compare(a, b))
    
    def test_constant_time_compare_different(self):
        """Test constant-time comparison with different inputs."""
        a = b"secret_key_12345"
        b = b"secret_key_54321"
        self.assertFalse(TimingAttackPrevention.constant_time_compare(a, b))
    
    def test_constant_time_compare_different_lengths(self):
        """Test constant-time comparison with different length inputs."""
        a = b"short"
        b = b"longer_string"
        self.assertFalse(TimingAttackPrevention.constant_time_compare(a, b))
    
    def test_constant_time_compare_timing_resistance(self):
        """Verify timing variance is minimal regardless of difference position."""
        key = b"0" * 1000
        
        # Early difference (position 0)
        early_diff = b"X" + b"0" * 999
        
        # Late difference (position 999)
        late_diff = b"0" * 999 + b"X"
        
        # Measure timing for both
        early_times = []
        late_times = []
        
        for _ in range(100):
            start = time.perf_counter()
            TimingAttackPrevention.constant_time_compare(key, early_diff)
            early_times.append(time.perf_counter() - start)
            
            start = time.perf_counter()
            TimingAttackPrevention.constant_time_compare(key, late_diff)
            late_times.append(time.perf_counter() - start)
        
        early_mean = statistics.mean(early_times)
        late_mean = statistics.mean(late_times)
        
        # Timing difference should be minimal (within 10% for constant-time)
        time_diff_ratio = abs(early_mean - late_mean) / max(early_mean, late_mean)
        self.assertLess(time_diff_ratio, 0.1, 
                       f"Timing variance too high: {time_diff_ratio:.2%}")
    
    def test_constant_time_select_true(self):
        """Test constant-time select with True condition."""
        result = TimingAttackPrevention.constant_time_select(True, 42, 99)
        self.assertEqual(result, 42)
    
    def test_constant_time_select_false(self):
        """Test constant-time select with False condition."""
        result = TimingAttackPrevention.constant_time_select(False, 42, 99)
        self.assertEqual(result, 99)
    
    def test_constant_time_array_access(self):
        """Test constant-time array access."""
        array = [10, 20, 30, 40, 50]
        
        # Test each index
        for i in range(len(array)):
            result = TimingAttackPrevention.constant_time_array_access(array, i)
            self.assertEqual(result, array[i])
    
    def test_constant_time_array_access_timing(self):
        """Verify array access timing is constant regardless of index."""
        array = list(range(100))
        
        # Measure timing for first and last index
        first_times = []
        last_times = []
        
        for _ in range(50):
            start = time.perf_counter()
            TimingAttackPrevention.constant_time_array_access(array, 0)
            first_times.append(time.perf_counter() - start)
            
            start = time.perf_counter()
            TimingAttackPrevention.constant_time_array_access(array, 99)
            last_times.append(time.perf_counter() - start)
        
        first_mean = statistics.mean(first_times)
        last_mean = statistics.mean(last_times)
        
        # Timing should be similar (within 15% for constant-time access)
        time_diff_ratio = abs(first_mean - last_mean) / max(first_mean, last_mean)
        self.assertLess(time_diff_ratio, 0.15,
                       f"Array access timing variance too high: {time_diff_ratio:.2%}")


class TestPowerAnalysisDefense(unittest.TestCase):
    """Test masking/blinding techniques."""
    
    def test_additive_masking_unmask(self):
        """Test additive masking and unmasking."""
        secret = 12345
        masked, mask = PowerAnalysisDefense.additive_masking(secret, 32)
        recovered = PowerAnalysisDefense.unmask(masked, mask, 32)
        self.assertEqual(recovered, secret)
    
    def test_additive_masking_randomness(self):
        """Verify additive masking produces different masks."""
        secret = 12345
        masks = set()
        
        for _ in range(100):
            masked, mask = PowerAnalysisDefense.additive_masking(secret, 32)
            masks.add(mask)
        
        # Should generate mostly unique masks (>90% unique)
        self.assertGreater(len(masks), 90)
    
    def test_boolean_masking_unmask(self):
        """Test boolean masking and unmasking."""
        secret = 12345
        masked, mask = PowerAnalysisDefense.boolean_masking(secret, 32)
        recovered = masked ^ mask
        self.assertEqual(recovered, secret)
    
    def test_boolean_masking_randomness(self):
        """Verify boolean masking produces different masks."""
        secret = 12345
        masks = set()
        
        for _ in range(100):
            masked, mask = PowerAnalysisDefense.boolean_masking(secret, 32)
            masks.add(mask)
        
        # Should generate mostly unique masks
        self.assertGreater(len(masks), 90)
    
    def test_masked_multiplication(self):
        """Test multiplication with masking."""
        test_cases = [
            (123, 456),
            (1, 1),
            (100, 200),
            (0, 12345),
        ]
        
        for a, b in test_cases:
            result = PowerAnalysisDefense.masked_multiplication(a, b, 32)
            expected = (a * b) % (2 ** 32)
            self.assertEqual(result, expected,
                           f"Masked multiplication failed: {a} * {b}")


class TestCacheTimingDefense(unittest.TestCase):
    """Test cache-oblivious algorithms."""
    
    def test_cache_oblivious_lookup(self):
        """Test cache-oblivious table lookup."""
        table = [100, 200, 300, 400, 500]
        
        for i in range(len(table)):
            result = CacheTimingDefense.cache_oblivious_lookup(table, i)
            self.assertEqual(result, table[i])
    
    def test_cache_oblivious_lookup_timing(self):
        """Verify lookup timing is independent of index."""
        table = list(range(1000))
        
        # Measure timing for different indices
        first_times = []
        middle_times = []
        last_times = []
        
        for _ in range(30):
            start = time.perf_counter()
            CacheTimingDefense.cache_oblivious_lookup(table, 0)
            first_times.append(time.perf_counter() - start)
            
            start = time.perf_counter()
            CacheTimingDefense.cache_oblivious_lookup(table, 500)
            middle_times.append(time.perf_counter() - start)
            
            start = time.perf_counter()
            CacheTimingDefense.cache_oblivious_lookup(table, 999)
            last_times.append(time.perf_counter() - start)
        
        first_mean = statistics.mean(first_times)
        middle_mean = statistics.mean(middle_times)
        last_mean = statistics.mean(last_times)
        
        # All should be similar (within 20% due to cache effects)
        max_mean = max(first_mean, middle_mean, last_mean)
        min_mean = min(first_mean, middle_mean, last_mean)
        variance_ratio = (max_mean - min_mean) / max_mean
        
        self.assertLess(variance_ratio, 0.2,
                       f"Cache-oblivious lookup variance too high: {variance_ratio:.2%}")
    
    def test_scatter_gather_load(self):
        """Test scatter-gather memory access."""
        data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        indices = [0, 3, 7, 9]
        expected = [data[i] for i in indices]
        
        result = CacheTimingDefense.scatter_gather_load(data, indices)
        self.assertEqual(result, expected)


class TestSideChannelBenchmark(unittest.TestCase):
    """Test benchmarking utilities."""
    
    def test_timing_variance_test(self):
        """Test timing variance measurement."""
        def test_func(a, b):
            return a + b
        
        stats = SideChannelBenchmark.timing_variance_test(test_func, 1, 2, trials=50)
        
        # Verify all expected keys are present
        self.assertIn('mean', stats)
        self.assertIn('std_dev', stats)
        self.assertIn('min', stats)
        self.assertIn('max', stats)
        self.assertIn('variance', stats)
        self.assertIn('trials', stats)
        
        # Verify values are reasonable
        self.assertGreater(stats['mean'], 0)
        self.assertGreaterEqual(stats['std_dev'], 0)
        self.assertEqual(stats['trials'], 50)
    
    def test_cache_timing_test(self):
        """Test cache-timing measurement."""
        def test_func(x):
            return sum(x)
        
        data = list(range(1000))
        stats = SideChannelBenchmark.cache_timing_test(test_func, data, trials=20)
        
        # Verify expected keys
        self.assertIn('warm_cache_mean', stats)
        self.assertIn('cold_cache_mean', stats)
        self.assertIn('cache_sensitivity', stats)
        
        # Warm cache should generally be faster (negative or small positive sensitivity)
        # Though in practice this can vary due to system noise
        self.assertIsInstance(stats['cache_sensitivity'], float)


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple mitigations."""
    
    def test_secure_authentication_flow(self):
        """Test complete authentication with side-channel resistance."""
        # Stored password hash (simulated)
        stored_hash = b"hashed_password_12345678"
        
        # User input
        user_input = b"hashed_password_12345678"
        
        # Constant-time comparison
        is_valid = TimingAttackPrevention.constant_time_compare(stored_hash, user_input)
        self.assertTrue(is_valid)
        
        # Mask sensitive session token generation
        session_token = 98765
        masked_token, mask = PowerAnalysisDefense.additive_masking(session_token, 32)
        
        # Process masked token (simulated)
        processed = masked_token  # In practice, perform operations on masked value
        
        # Unmask result
        final_token = PowerAnalysisDefense.unmask(processed, mask, 32)
        self.assertEqual(final_token, session_token)
    
    def test_secure_database_query(self):
        """Test database query with cache-timing resistance."""
        # Simulated database table
        user_records = [
            {"id": 1, "balance": 1000},
            {"id": 2, "balance": 2000},
            {"id": 3, "balance": 3000},
            {"id": 4, "balance": 5000},
        ]
        
        # Convert to list for cache-oblivious access
        balances = [rec["balance"] for rec in user_records]
        
        # Query user 2's balance (secret index = 1)
        secret_user_index = 1
        balance = CacheTimingDefense.cache_oblivious_lookup(balances, secret_user_index)
        
        self.assertEqual(balance, 2000)


def run_performance_tests():
    """Run performance comparisons."""
    print("\n=== PERFORMANCE COMPARISONS ===\n")
    
    # 1. Constant-time vs naive comparison
    key = b"0" * 1000
    input1 = b"0" * 1000
    input2 = b"X" + b"0" * 999
    
    print("1. String Comparison (1000 bytes)")
    
    # Constant-time
    start = time.perf_counter()
    for _ in range(1000):
        TimingAttackPrevention.constant_time_compare(key, input1)
    ct_time = time.perf_counter() - start
    
    # Naive (for comparison only - VULNERABLE!)
    start = time.perf_counter()
    for _ in range(1000):
        key == input1
    naive_time = time.perf_counter() - start
    
    print(f"   Constant-time: {ct_time*1000:.2f} ms (1000 iterations)")
    print(f"   Naive:         {naive_time*1000:.2f} ms (1000 iterations)")
    print(f"   Overhead:      {(ct_time/naive_time - 1)*100:.1f}%\n")
    
    # 2. Cache-oblivious lookup
    table = list(range(1000))
    
    print("2. Array Lookup (1000 elements)")
    
    # Cache-oblivious
    start = time.perf_counter()
    for i in range(100):
        CacheTimingDefense.cache_oblivious_lookup(table, i % len(table))
    co_time = time.perf_counter() - start
    
    # Direct access (for comparison - VULNERABLE!)
    start = time.perf_counter()
    for i in range(100):
        _ = table[i % len(table)]
    direct_time = time.perf_counter() - start
    
    print(f"   Cache-oblivious: {co_time*1000:.2f} ms (100 lookups)")
    print(f"   Direct access:   {direct_time*1000:.2f} ms (100 lookups)")
    print(f"   Overhead:        {(co_time/direct_time - 1)*100:.1f}%\n")


if __name__ == "__main__":
    # Run unit tests
    print("=== RUNNING UNIT TESTS ===\n")
    unittest.main(argv=[''], verbosity=2, exit=False)
    
    # Run performance tests
    run_performance_tests()
    
    print("✅ All tests completed!")
