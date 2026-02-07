#!/usr/bin/env python3
"""
JWT Token Validator
Production-ready security tool for validating and analyzing JWT tokens
"""

import json
import base64
import hmac
import hashlib
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class JWTValidation:
    """Results of JWT validation"""
    valid: bool
    decoded_header: Dict
    decoded_payload: Dict
    issues: List[str]
    warnings: List[str]
    security_score: int  # 0-100
    expires_in: Optional[str]
    algorithm: str


class JWTValidator:
    """Validate and analyze JWT tokens for security issues"""
    
    # Weak/insecure algorithms
    WEAK_ALGORITHMS = ['none', 'HS256']  # HS256 vulnerable to key confusion
    
    # Recommended algorithms
    STRONG_ALGORITHMS = ['RS256', 'RS384', 'RS512', 'ES256', 'ES384', 'ES512']
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize JWT validator
        
        Args:
            secret_key: Optional secret key for HMAC validation
        """
        self.secret_key = secret_key
        self.total_validated = 0
        self.invalid_count = 0
    
    def validate(self, token: str, verify_signature: bool = False) -> JWTValidation:
        """
        Validate JWT token structure and security
        
        Args:
            token: JWT token string
            verify_signature: Whether to verify signature (requires secret_key)
            
        Returns:
            JWTValidation with validation results
        """
        self.total_validated += 1
        
        issues = []
        warnings = []
        security_score = 100
        
        # Parse token structure
        try:
            parts = token.split('.')
            if len(parts) != 3:
                issues.append(f"Invalid JWT structure: expected 3 parts, got {len(parts)}")
                self.invalid_count += 1
                return self._create_invalid_result(issues)
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Decode header
            try:
                header = self._decode_base64(header_b64)
                decoded_header = json.loads(header)
            except Exception as e:
                issues.append(f"Failed to decode header: {str(e)}")
                self.invalid_count += 1
                return self._create_invalid_result(issues)
            
            # Decode payload
            try:
                payload = self._decode_base64(payload_b64)
                decoded_payload = json.loads(payload)
            except Exception as e:
                issues.append(f"Failed to decode payload: {str(e)}")
                self.invalid_count += 1
                return self._create_invalid_result(issues)
            
        except Exception as e:
            issues.append(f"Failed to parse token: {str(e)}")
            self.invalid_count += 1
            return self._create_invalid_result(issues)
        
        # Validate header
        algorithm = decoded_header.get('alg', 'unknown')
        
        if algorithm == 'none':
            issues.append("CRITICAL: Algorithm is 'none' (no signature)")
            security_score -= 50
        elif algorithm in self.WEAK_ALGORITHMS:
            warnings.append(f"Weak algorithm: {algorithm}")
            security_score -= 20
        elif algorithm not in self.STRONG_ALGORITHMS:
            warnings.append(f"Unknown algorithm: {algorithm}")
            security_score -= 10
        
        # Check for typ claim
        if 'typ' not in decoded_header:
            warnings.append("Missing 'typ' claim in header")
            security_score -= 5
        elif decoded_header['typ'] != 'JWT':
            warnings.append(f"Unexpected typ: {decoded_header['typ']}")
        
        # Validate payload claims
        current_time = int(time.time())
        
        # Check expiration (exp)
        expires_in = None
        if 'exp' in decoded_payload:
            exp = decoded_payload['exp']
            if exp < current_time:
                issues.append(f"Token expired at {datetime.fromtimestamp(exp)}")
                security_score -= 30
            else:
                exp_delta = exp - current_time
                expires_in = self._format_time_delta(exp_delta)
                if exp_delta > 86400 * 30:  # >30 days
                    warnings.append("Token expires in >30 days (long expiration)")
                    security_score -= 10
        else:
            warnings.append("No expiration claim (exp)")
            security_score -= 15
        
        # Check not-before (nbf)
        if 'nbf' in decoded_payload:
            nbf = decoded_payload['nbf']
            if nbf > current_time:
                issues.append(f"Token not yet valid (nbf: {datetime.fromtimestamp(nbf)})")
                security_score -= 20
        
        # Check issued-at (iat)
        if 'iat' not in decoded_payload:
            warnings.append("No issued-at claim (iat)")
            security_score -= 5
        else:
            iat = decoded_payload['iat']
            if iat > current_time:
                warnings.append("Issued-at is in the future")
                security_score -= 10
        
        # Check issuer (iss)
        if 'iss' not in decoded_payload:
            warnings.append("No issuer claim (iss)")
            security_score -= 5
        
        # Check subject (sub)
        if 'sub' not in decoded_payload:
            warnings.append("No subject claim (sub)")
            security_score -= 5
        
        # Check audience (aud)
        if 'aud' not in decoded_payload:
            warnings.append("No audience claim (aud)")
            security_score -= 5
        
        # Check for sensitive data in payload
        sensitive_keys = ['password', 'secret', 'api_key', 'private_key', 'ssn', 'credit_card']
        for key in decoded_payload.keys():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                warnings.append(f"Potential sensitive data in payload: {key}")
                security_score -= 15
        
        # Verify signature if requested
        if verify_signature:
            if not self.secret_key:
                warnings.append("Signature verification requested but no secret key provided")
            else:
                if not self._verify_signature(token, algorithm):
                    issues.append("CRITICAL: Signature verification failed")
                    security_score -= 40
        
        # Check payload size
        payload_size = len(payload_b64)
        if payload_size > 8192:  # >8KB
            warnings.append(f"Large payload size: {payload_size} bytes")
            security_score -= 10
        
        # Determine validity
        valid = len(issues) == 0
        if not valid:
            self.invalid_count += 1
        
        security_score = max(0, security_score)
        
        return JWTValidation(
            valid=valid,
            decoded_header=decoded_header,
            decoded_payload=decoded_payload,
            issues=issues,
            warnings=warnings,
            security_score=security_score,
            expires_in=expires_in,
            algorithm=algorithm
        )
    
    def _decode_base64(self, b64_string: str) -> str:
        """Decode base64url string"""
        # Add padding if needed
        padding = 4 - (len(b64_string) % 4)
        if padding != 4:
            b64_string += '=' * padding
        
        # Replace URL-safe characters
        b64_string = b64_string.replace('-', '+').replace('_', '/')
        
        return base64.b64decode(b64_string).decode('utf-8')
    
    def _verify_signature(self, token: str, algorithm: str) -> bool:
        """Verify HMAC signature (HS256/HS384/HS512)"""
        if algorithm not in ['HS256', 'HS384', 'HS512']:
            return False  # Can't verify other algorithms without public key
        
        parts = token.split('.')
        if len(parts) != 3:
            return False
        
        message = f"{parts[0]}.{parts[1]}"
        signature_b64 = parts[2]
        
        # Choose hash algorithm
        if algorithm == 'HS256':
            hash_func = hashlib.sha256
        elif algorithm == 'HS384':
            hash_func = hashlib.sha384
        else:  # HS512
            hash_func = hashlib.sha512
        
        # Compute expected signature
        expected_sig = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hash_func
        ).digest()
        
        # Encode to base64url
        expected_b64 = base64.urlsafe_b64encode(expected_sig).decode('utf-8').rstrip('=')
        
        return hmac.compare_digest(expected_b64, signature_b64)
    
    def _create_invalid_result(self, issues: List[str]) -> JWTValidation:
        """Create result for invalid token"""
        return JWTValidation(
            valid=False,
            decoded_header={},
            decoded_payload={},
            issues=issues,
            warnings=[],
            security_score=0,
            expires_in=None,
            algorithm='unknown'
        )
    
    def _format_time_delta(self, seconds: int) -> str:
        """Format time delta in human-readable form"""
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            return f"{seconds // 60} minutes"
        elif seconds < 86400:
            return f"{seconds // 3600} hours"
        else:
            return f"{seconds // 86400} days"
    
    def decode_without_verification(self, token: str) -> Tuple[Dict, Dict]:
        """
        Decode JWT without verification (for inspection only)
        
        Returns:
            (header, payload) tuple
        """
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT structure")
        
        header = json.loads(self._decode_base64(parts[0]))
        payload = json.loads(self._decode_base64(parts[1]))
        
        return header, payload
    
    def get_stats(self) -> Dict:
        """Get validator statistics"""
        return {
            'total_validated': self.total_validated,
            'invalid_count': self.invalid_count,
            'valid_count': self.total_validated - self.invalid_count,
            'invalid_percentage': (self.invalid_count / self.total_validated * 100) if self.total_validated > 0 else 0
        }


def validate_jwt(token: str, secret: Optional[str] = None) -> Dict:
    """
    Convenience function for JWT validation
    
    Args:
        token: JWT token string
        secret: Optional secret key for signature verification
        
    Returns:
        Dict with validation results
    """
    validator = JWTValidator(secret_key=secret)
    result = validator.validate(token, verify_signature=bool(secret))
    
    return {
        'valid': result.valid,
        'header': result.decoded_header,
        'payload': result.decoded_payload,
        'issues': result.issues,
        'warnings': result.warnings,
        'security_score': result.security_score,
        'expires_in': result.expires_in,
        'algorithm': result.algorithm
    }


if __name__ == "__main__":
    # Demo usage
    print("="*60)
    print("JWT VALIDATOR - Demo")
    print("="*60)
    
    # Example tokens (for demonstration)
    test_tokens = {
        "Valid Token (no signature check)": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjk5OTk5OTk5OTl9.signature",
        "No Algorithm": "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0.",
        "Expired Token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiZXhwIjoxNTE2MjM5MDIyfQ.signature"
    }
    
    validator = JWTValidator()
    
    for name, token in test_tokens.items():
        print(f"\n{name}:")
        result = validator.validate(token)
        print(f"  Valid: {result.valid}")
        print(f"  Security Score: {result.security_score}/100")
        print(f"  Algorithm: {result.algorithm}")
        if result.expires_in:
            print(f"  Expires in: {result.expires_in}")
        if result.issues:
            print(f"  Issues: {', '.join(result.issues)}")
        if result.warnings:
            print(f"  Warnings: {result.warnings[0]}")
    
    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    stats = validator.get_stats()
    print(f"Total validated: {stats['total_validated']}")
    print(f"Invalid tokens: {stats['invalid_count']} ({stats['invalid_percentage']:.1f}%)")
