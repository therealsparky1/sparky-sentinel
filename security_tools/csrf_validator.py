#!/usr/bin/env python3
"""
CSRF (Cross-Site Request Forgery) Token Validator
Production-ready security tool for CSRF protection
"""

import hmac
import hashlib
import secrets
import time
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class TokenStatus(Enum):
    """CSRF token validation status"""
    VALID = "valid"
    EXPIRED = "expired"
    INVALID = "invalid"
    MISSING = "missing"
    REUSED = "reused"


@dataclass
class CSRFValidation:
    """Results of CSRF token validation"""
    status: TokenStatus
    valid: bool
    token: Optional[str]
    age_seconds: Optional[int]
    issues: list[str]
    recommendations: list[str]


class CSRFTokenValidator:
    """Generate and validate CSRF tokens"""
    
    # Token configuration
    DEFAULT_EXPIRY = 3600  # 1 hour
    TOKEN_LENGTH = 32  # 256 bits
    
    def __init__(self, secret_key: str, token_expiry: int = DEFAULT_EXPIRY):
        """
        Initialize CSRF validator
        
        Args:
            secret_key: Secret key for HMAC signing
            token_expiry: Token expiration time in seconds
        """
        self.secret_key = secret_key.encode('utf-8')
        self.token_expiry = token_expiry
        
        # Token tracking (in production, use Redis or database)
        self.issued_tokens = {}  # {token: timestamp}
        self.used_tokens = set()  # One-time use enforcement
        
        # Statistics
        self.total_generated = 0
        self.total_validated = 0
        self.valid_count = 0
        self.invalid_count = 0
    
    def generate_token(self, session_id: str) -> str:
        """
        Generate CSRF token for a session
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            CSRF token string
        """
        self.total_generated += 1
        
        # Generate random token
        random_part = secrets.token_urlsafe(self.TOKEN_LENGTH)
        
        # Current timestamp
        timestamp = int(time.time())
        
        # Create message: session_id:timestamp:random
        message = f"{session_id}:{timestamp}:{random_part}"
        
        # Generate HMAC signature
        signature = hmac.new(
            self.secret_key,
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()[:16]  # First 16 chars
        
        # Token format: timestamp.random.signature
        token = f"{timestamp}.{random_part}.{signature}"
        
        # Store token
        self.issued_tokens[token] = timestamp
        
        # Cleanup old tokens periodically
        if len(self.issued_tokens) > 10000:
            self._cleanup_old_tokens()
        
        return token
    
    def validate_token(
        self,
        token: Optional[str],
        session_id: str,
        allow_reuse: bool = False
    ) -> CSRFValidation:
        """
        Validate CSRF token
        
        Args:
            token: CSRF token to validate
            session_id: Session ID associated with the token
            allow_reuse: Whether to allow token reuse (default: False)
            
        Returns:
            CSRFValidation with validation results
        """
        self.total_validated += 1
        
        issues = []
        recommendations = []
        
        # Check if token is provided
        if not token:
            self.invalid_count += 1
            return CSRFValidation(
                status=TokenStatus.MISSING,
                valid=False,
                token=None,
                age_seconds=None,
                issues=["CSRF token not provided"],
                recommendations=["Include CSRF token in all state-changing requests"]
            )
        
        # Parse token
        try:
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            timestamp_str, random_part, signature = parts
            timestamp = int(timestamp_str)
        except Exception as e:
            self.invalid_count += 1
            return CSRFValidation(
                status=TokenStatus.INVALID,
                valid=False,
                token=token,
                age_seconds=None,
                issues=[f"Malformed token: {str(e)}"],
                recommendations=["Ensure token is not corrupted"]
            )
        
        # Check if token was issued by us
        if token not in self.issued_tokens:
            self.invalid_count += 1
            issues.append("Token was not issued by this server")
            return CSRFValidation(
                status=TokenStatus.INVALID,
                valid=False,
                token=token,
                age_seconds=None,
                issues=issues,
                recommendations=["Generate new token from server"]
            )
        
        # Verify HMAC signature
        message = f"{session_id}:{timestamp}:{random_part}"
        expected_sig = hmac.new(
            self.secret_key,
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()[:16]
        
        if not hmac.compare_digest(signature, expected_sig):
            self.invalid_count += 1
            issues.append("Token signature verification failed")
            return CSRFValidation(
                status=TokenStatus.INVALID,
                valid=False,
                token=token,
                age_seconds=None,
                issues=issues,
                recommendations=["Token may be tampered with or from different session"]
            )
        
        # Check expiration
        current_time = int(time.time())
        age_seconds = current_time - timestamp
        
        if age_seconds > self.token_expiry:
            self.invalid_count += 1
            issues.append(f"Token expired ({age_seconds}s old, max {self.token_expiry}s)")
            recommendations.append("Generate new token for continued use")
            return CSRFValidation(
                status=TokenStatus.EXPIRED,
                valid=False,
                token=token,
                age_seconds=age_seconds,
                issues=issues,
                recommendations=recommendations
            )
        
        # Check for reuse (one-time use)
        if not allow_reuse and token in self.used_tokens:
            self.invalid_count += 1
            issues.append("Token has already been used (potential replay attack)")
            recommendations.append("Generate new token after each use")
            return CSRFValidation(
                status=TokenStatus.REUSED,
                valid=False,
                token=token,
                age_seconds=age_seconds,
                issues=issues,
                recommendations=recommendations
            )
        
        # Mark token as used
        if not allow_reuse:
            self.used_tokens.add(token)
        
        # Token is valid
        self.valid_count += 1
        
        # Generate warnings if token is close to expiring
        if age_seconds > self.token_expiry * 0.8:
            recommendations.append(f"Token will expire soon (in {self.token_expiry - age_seconds}s)")
        
        return CSRFValidation(
            status=TokenStatus.VALID,
            valid=True,
            token=token,
            age_seconds=age_seconds,
            issues=[],
            recommendations=recommendations
        )
    
    def _cleanup_old_tokens(self):
        """Remove expired tokens from storage"""
        current_time = int(time.time())
        cutoff_time = current_time - self.token_expiry
        
        # Remove expired issued tokens
        self.issued_tokens = {
            token: ts
            for token, ts in self.issued_tokens.items()
            if ts > cutoff_time
        }
        
        # Remove old used tokens
        # (In production, implement TTL-based cleanup)
        if len(self.used_tokens) > 10000:
            self.used_tokens.clear()
    
    def revoke_token(self, token: str):
        """Revoke a specific token"""
        if token in self.issued_tokens:
            del self.issued_tokens[token]
        self.used_tokens.add(token)
    
    def revoke_session_tokens(self, session_id: str):
        """Revoke all tokens for a session"""
        # Note: This simplified implementation doesn't store session_id mapping
        # In production, maintain session_id -> [tokens] mapping
        self.issued_tokens.clear()
        self.used_tokens.clear()
    
    def get_stats(self) -> Dict:
        """Get validator statistics"""
        return {
            'total_generated': self.total_generated,
            'total_validated': self.total_validated,
            'valid_count': self.valid_count,
            'invalid_count': self.invalid_count,
            'active_tokens': len(self.issued_tokens),
            'used_tokens': len(self.used_tokens),
            'validation_success_rate': (self.valid_count / self.total_validated * 100) if self.total_validated > 0 else 0
        }


# Convenience functions
def generate_csrf_token(session_id: str, secret: str = None) -> str:
    """Generate CSRF token"""
    if not secret:
        secret = secrets.token_urlsafe(32)
    validator = CSRFTokenValidator(secret)
    return validator.generate_token(session_id)


def validate_csrf_token(token: str, session_id: str, secret: str) -> Dict:
    """Validate CSRF token"""
    validator = CSRFTokenValidator(secret)
    
    # Need to add token to issued_tokens for validation
    # (In production, tokens persist in database/cache)
    parts = token.split('.')
    if len(parts) == 3:
        try:
            timestamp = int(parts[0])
            validator.issued_tokens[token] = timestamp
        except:
            pass
    
    result = validator.validate_token(token, session_id)
    
    return {
        'valid': result.valid,
        'status': result.status.value,
        'age_seconds': result.age_seconds,
        'issues': result.issues,
        'recommendations': result.recommendations
    }


if __name__ == "__main__":
    # Demo usage
    print("="*60)
    print("CSRF TOKEN VALIDATOR - Demo")
    print("="*60)
    
    # Initialize validator with secret
    secret = "my-super-secret-key-change-in-production"
    validator = CSRFTokenValidator(secret, token_expiry=60)  # 60s expiry for demo
    
    session_id = "user123"
    
    # Generate token
    print(f"\n1. Generating CSRF token for session: {session_id}")
    token = validator.generate_token(session_id)
    print(f"   Token: {token[:40]}...")
    
    # Validate token (should pass)
    print(f"\n2. Validating token (should be VALID):")
    result = validator.validate_token(token, session_id)
    print(f"   Status: {result.status.value.upper()}")
    print(f"   Valid: {result.valid}")
    print(f"   Age: {result.age_seconds}s")
    
    # Try to reuse token (should fail)
    print(f"\n3. Reusing token (should be REUSED):")
    result = validator.validate_token(token, session_id)
    print(f"   Status: {result.status.value.upper()}")
    print(f"   Valid: {result.valid}")
    if result.issues:
        print(f"   Issue: {result.issues[0]}")
    
    # Try invalid token
    print(f"\n4. Validating invalid token:")
    result = validator.validate_token("invalid.token.here", session_id)
    print(f"   Status: {result.status.value.upper()}")
    print(f"   Valid: {result.valid}")
    if result.issues:
        print(f"   Issue: {result.issues[0]}")
    
    # Simulate expiration (wait or manipulate timestamp)
    print(f"\n5. Simulating expired token:")
    old_token = f"{int(time.time()) - 120}.random.signature"  # 120s old
    validator.issued_tokens[old_token] = int(time.time()) - 120
    result = validator.validate_token(old_token, session_id)
    print(f"   Status: {result.status.value.upper()}")
    print(f"   Valid: {result.valid}")
    if result.issues:
        print(f"   Issue: {result.issues[0]}")
    
    # Statistics
    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    stats = validator.get_stats()
    print(f"Tokens generated: {stats['total_generated']}")
    print(f"Validations: {stats['total_validated']}")
    print(f"Valid: {stats['valid_count']}")
    print(f"Invalid: {stats['invalid_count']}")
    print(f"Success rate: {stats['validation_success_rate']:.1f}%")
    print(f"Active tokens: {stats['active_tokens']}")
