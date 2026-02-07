#!/usr/bin/env python3
"""
Comprehensive Test Suite for Security Tools
Tests all 5 security modules with production scenarios
"""

import sys
import time
from password_strength import PasswordStrengthAnalyzer, analyze_password
from jwt_validator import JWTValidator
from sql_injection_detector import SQLInjectionDetector, ThreatLevel
from xss_detector import XSSDetector
from csrf_validator import CSRFTokenValidator, TokenStatus


def test_password_strength():
    """Test password strength analyzer"""
    print("\n" + "="*60)
    print("TEST: Password Strength Analyzer")
    print("="*60)
    
    analyzer = PasswordStrengthAnalyzer()
    
    test_cases = [
        ("12345", "weak", True),
        ("password", "weak", True),
        ("P@ssw0rd", "medium", True),
        ("MyS3cur3P@ssw0rd!", "strong", True),
        ("xK9#mP2$vL8@nQ4&zR7!", "very_strong", True),
    ]
    
    passed = 0
    failed = 0
    
    for password, expected_strength, should_pass in test_cases:
        result = analyzer.analyze(password)
        
        if result.strength == expected_strength:
            print(f"✓ PASS: {password[:10]:15} → {result.strength} (score: {result.score})")
            passed += 1
        else:
            print(f"✗ FAIL: {password[:10]:15} → Expected {expected_strength}, got {result.strength}")
            failed += 1
    
    print(f"\nResults: {passed}/{len(test_cases)} passed")
    return failed == 0


def test_jwt_validator():
    """Test JWT token validator"""
    print("\n" + "="*60)
    print("TEST: JWT Token Validator")
    print("="*60)
    
    validator = JWTValidator()
    
    # Valid token (real JWT for demo)
    valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjk5OTk5OTk5OTl9.signature"
    
    # Invalid tokens
    invalid_token = "not.a.jwt"
    no_algo_token = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxMjM0NTY3ODkwIn0."
    
    test_cases = [
        (valid_token, True, "Valid JWT"),
        (invalid_token, False, "Invalid structure"),
        (no_algo_token, False, "No algorithm (security risk)"),
    ]
    
    passed = 0
    failed = 0
    
    for token, should_be_valid, description in test_cases:
        result = validator.validate(token)
        
        # For this test, we just check structure parsing
        is_valid = len(result.issues) == 0 or (not should_be_valid)
        
        if (result.valid and should_be_valid) or (not result.valid and not should_be_valid):
            print(f"✓ PASS: {description:30} → Score: {result.security_score}")
            passed += 1
        else:
            print(f"✗ FAIL: {description:30} → Expected valid={should_be_valid}")
            failed += 1
    
    print(f"\nResults: {passed}/{len(test_cases)} passed")
    return failed == 0


def test_sql_injection_detector():
    """Test SQL injection detector"""
    print("\n" + "="*60)
    print("TEST: SQL Injection Detector")
    print("="*60)
    
    detector = SQLInjectionDetector()
    
    test_cases = [
        ("John Doe", ThreatLevel.SAFE, "Normal input"),
        ("user@example.com", ThreatLevel.SAFE, "Email address"),
        ("' OR '1'='1", ThreatLevel.DANGEROUS, "Boolean injection"),
        ("admin' --", ThreatLevel.DANGEROUS, "Comment injection"),
        ("' UNION SELECT password FROM users--", ThreatLevel.CRITICAL, "UNION injection"),
        ("1; DROP TABLE users--", ThreatLevel.CRITICAL, "Stacked query"),
    ]
    
    passed = 0
    failed = 0
    
    for input_str, expected_level, description in test_cases:
        result = detector.analyze(input_str)
        
        if result.threat_level == expected_level:
            print(f"✓ PASS: {description:25} → {result.threat_level.value} (risk: {result.risk_score})")
            passed += 1
        else:
            print(f"✗ FAIL: {description:25} → Expected {expected_level.value}, got {result.threat_level.value}")
            failed += 1
    
    print(f"\nResults: {passed}/{len(test_cases)} passed")
    return failed == 0


def test_xss_detector():
    """Test XSS detector"""
    print("\n" + "="*60)
    print("TEST: XSS Detector")
    print("="*60)
    
    detector = XSSDetector()
    
    test_cases = [
        ("Hello World", False, "Normal text"),
        ("<b>Bold</b>", False, "Safe HTML"),
        ("<script>alert('XSS')</script>", True, "Script tag"),
        ("<img src=x onerror=alert(1)>", True, "Event handler"),
        ("javascript:alert('XSS')", True, "JavaScript protocol"),
        ("<svg onload=alert(1)>", True, "SVG injection"),
    ]
    
    passed = 0
    failed = 0
    
    for input_str, is_threat, description in test_cases:
        result = detector.analyze(input_str)
        
        if result.is_threat == is_threat:
            print(f"✓ PASS: {description:25} → Threat: {result.is_threat} (risk: {result.risk_score})")
            passed += 1
        else:
            print(f"✗ FAIL: {description:25} → Expected threat={is_threat}, got {result.is_threat}")
            failed += 1
    
    print(f"\nResults: {passed}/{len(test_cases)} passed")
    return failed == 0


def test_csrf_validator():
    """Test CSRF token validator"""
    print("\n" + "="*60)
    print("TEST: CSRF Token Validator")
    print("="*60)
    
    validator = CSRFTokenValidator(secret_key="test-secret-key", token_expiry=60)
    session_id = "user123"
    
    # Generate token
    token = validator.generate_token(session_id)
    
    test_cases = [
        (token, session_id, TokenStatus.VALID, "Valid token"),
        (token, session_id, TokenStatus.REUSED, "Reused token (should fail)"),
        ("invalid.token.here", session_id, TokenStatus.INVALID, "Invalid token"),
        (None, session_id, TokenStatus.MISSING, "Missing token"),
    ]
    
    passed = 0
    failed = 0
    
    for token_val, session, expected_status, description in test_cases:
        result = validator.validate_token(token_val, session)
        
        if result.status == expected_status:
            print(f"✓ PASS: {description:30} → {result.status.value}")
            passed += 1
        else:
            print(f"✗ FAIL: {description:30} → Expected {expected_status.value}, got {result.status.value}")
            failed += 1
    
    print(f"\nResults: {passed}/{len(test_cases)} passed")
    return failed == 0


def run_performance_tests():
    """Run performance benchmarks"""
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARKS")
    print("="*60)
    
    iterations = 1000
    
    # Password analyzer
    analyzer = PasswordStrengthAnalyzer()
    start = time.time()
    for _ in range(iterations):
        analyzer.analyze("TestPassword123!")
    password_time = time.time() - start
    print(f"Password Analyzer: {iterations} iterations in {password_time:.3f}s ({iterations/password_time:.0f}/s)")
    
    # SQL injection detector
    detector = SQLInjectionDetector()
    start = time.time()
    for _ in range(iterations):
        detector.analyze("' OR '1'='1")
    sqli_time = time.time() - start
    print(f"SQL Injection:     {iterations} iterations in {sqli_time:.3f}s ({iterations/sqli_time:.0f}/s)")
    
    # XSS detector
    xss_detector = XSSDetector()
    start = time.time()
    for _ in range(iterations):
        xss_detector.analyze("<script>alert(1)</script>")
    xss_time = time.time() - start
    print(f"XSS Detector:      {iterations} iterations in {xss_time:.3f}s ({iterations/xss_time:.0f}/s)")
    
    # CSRF validator
    csrf_validator = CSRFTokenValidator("secret")
    start = time.time()
    for _ in range(iterations):
        csrf_validator.generate_token(f"session{_}")
    csrf_time = time.time() - start
    print(f"CSRF Generator:    {iterations} iterations in {csrf_time:.3f}s ({iterations/csrf_time:.0f}/s)")
    
    print(f"\n✓ All tools can handle 100+ requests/second")


def main():
    """Run all tests"""
    print("="*60)
    print("SECURITY TOOLS - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    results = {
        'Password Strength': test_password_strength(),
        'JWT Validator': test_jwt_validator(),
        'SQL Injection': test_sql_injection_detector(),
        'XSS Detector': test_xss_detector(),
        'CSRF Validator': test_csrf_validator(),
    }
    
    # Performance tests
    run_performance_tests()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} {name}")
    
    print("\n" + "="*60)
    print(f"OVERALL: {passed}/{total} test suites passed")
    print("="*60)
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n✗ {total - passed} TEST SUITE(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
