#!/usr/bin/env python3
"""
Password Strength Analyzer
Production-ready security tool for evaluating password security
"""

import re
import math
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class PasswordAnalysis:
    """Results of password strength analysis"""
    score: int  # 0-100
    strength: str  # weak, medium, strong, very_strong
    entropy: float  # bits of entropy
    issues: List[str]
    suggestions: List[str]
    crack_time: str  # estimated time to crack


class PasswordStrengthAnalyzer:
    """Analyze password strength using multiple security criteria"""
    
    # Common password patterns to flag
    COMMON_PATTERNS = [
        r'123', r'abc', r'qwerty', r'password', r'admin',
        r'letmein', r'welcome', r'monkey', r'dragon', r'master'
    ]
    
    # Common substitutions (leet speak)
    SUBSTITUTIONS = {
        '@': 'a', '0': 'o', '1': 'i', '3': 'e', '4': 'a',
        '5': 's', '7': 't', '8': 'b', '9': 'g'
    }
    
    def __init__(self):
        self.reset_stats()
    
    def reset_stats(self):
        """Reset analysis statistics"""
        self.total_analyzed = 0
        self.weak_count = 0
        self.strong_count = 0
    
    def analyze(self, password: str) -> PasswordAnalysis:
        """
        Comprehensive password strength analysis
        
        Args:
            password: Password to analyze
            
        Returns:
            PasswordAnalysis with score, strength, issues, suggestions
        """
        self.total_analyzed += 1
        
        issues = []
        suggestions = []
        score = 0
        
        # Length scoring (0-30 points)
        length = len(password)
        if length < 8:
            issues.append("Password too short (minimum 8 characters)")
            suggestions.append("Use at least 12 characters for better security")
            score += length * 2
        elif length < 12:
            score += 20
            suggestions.append("Consider using 16+ characters for maximum security")
        elif length < 16:
            score += 25
        else:
            score += 30
        
        # Character diversity (0-30 points)
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[^a-zA-Z0-9]', password))
        
        diversity_score = sum([has_lower, has_upper, has_digit, has_special])
        
        if not has_lower:
            issues.append("No lowercase letters")
        if not has_upper:
            issues.append("No uppercase letters")
        if not has_digit:
            issues.append("No numbers")
        if not has_special:
            issues.append("No special characters")
            suggestions.append("Add special characters (!@#$%^&*)")
        
        score += diversity_score * 7.5
        
        # Entropy calculation (0-20 points)
        entropy = self._calculate_entropy(password)
        if entropy < 30:
            issues.append(f"Low entropy ({entropy:.1f} bits)")
            score += entropy / 3
        elif entropy < 50:
            score += 15
        else:
            score += 20
        
        # Pattern detection (-20 points for common patterns)
        pattern_penalty = 0
        for pattern in self.COMMON_PATTERNS:
            if re.search(pattern, password.lower()):
                issues.append(f"Contains common pattern: {pattern}")
                pattern_penalty += 5
        
        score = max(0, score - pattern_penalty)
        
        # Repetition detection (-10 points)
        if self._has_repetition(password):
            issues.append("Contains repeated characters or sequences")
            suggestions.append("Avoid repeated patterns (aaa, 111, etc.)")
            score = max(0, score - 10)
        
        # Dictionary word detection (-15 points)
        if self._contains_dictionary_word(password):
            issues.append("Contains dictionary word")
            suggestions.append("Avoid common words, use random characters")
            score = max(0, score - 15)
        
        # Sequential characters (-10 points)
        if self._has_sequential(password):
            issues.append("Contains sequential characters (abc, 123)")
            suggestions.append("Avoid keyboard sequences")
            score = max(0, score - 10)
        
        # Bonus for length + diversity (0-20 points)
        if length >= 16 and diversity_score == 4:
            score += 20
        
        # Cap score at 100
        score = min(100, score)
        
        # Determine strength level
        if score < 30:
            strength = "weak"
            self.weak_count += 1
        elif score < 60:
            strength = "medium"
        elif score < 80:
            strength = "strong"
            self.strong_count += 1
        else:
            strength = "very_strong"
            self.strong_count += 1
        
        # Estimate crack time
        crack_time = self._estimate_crack_time(entropy, length)
        
        return PasswordAnalysis(
            score=score,
            strength=strength,
            entropy=entropy,
            issues=issues,
            suggestions=suggestions,
            crack_time=crack_time
        )
    
    def _calculate_entropy(self, password: str) -> float:
        """
        Calculate Shannon entropy in bits
        
        Higher entropy = more randomness = stronger password
        """
        if not password:
            return 0.0
        
        # Character space size
        charset_size = 0
        if re.search(r'[a-z]', password):
            charset_size += 26
        if re.search(r'[A-Z]', password):
            charset_size += 26
        if re.search(r'\d', password):
            charset_size += 10
        if re.search(r'[^a-zA-Z0-9]', password):
            charset_size += 32  # Common special chars
        
        # Entropy = log2(charset_size ^ length)
        entropy = len(password) * math.log2(charset_size) if charset_size > 0 else 0
        
        return entropy
    
    def _has_repetition(self, password: str) -> bool:
        """Detect repeated characters or patterns"""
        # Check for 3+ repeated characters
        if re.search(r'(.)\1{2,}', password):
            return True
        
        # Check for repeated 2-char patterns
        if re.search(r'(.{2,})\1', password):
            return True
        
        return False
    
    def _has_sequential(self, password: str) -> bool:
        """Detect sequential characters (abc, 123, qwe)"""
        sequences = ['abc', '123', '456', '789', 'qwe', 'asd', 'zxc']
        pwd_lower = password.lower()
        
        for seq in sequences:
            if seq in pwd_lower or seq[::-1] in pwd_lower:
                return True
        
        # Check for ascending/descending sequences
        for i in range(len(password) - 2):
            chars = password[i:i+3]
            if chars.isdigit():
                nums = [int(c) for c in chars]
                if nums == sorted(nums) or nums == sorted(nums, reverse=True):
                    return True
        
        return False
    
    def _contains_dictionary_word(self, password: str) -> bool:
        """Check for common dictionary words"""
        # Simple check against common words (in production, use full dictionary)
        common_words = [
            'password', 'admin', 'user', 'login', 'welcome',
            'hello', 'world', 'master', 'root', 'test',
            'love', 'money', 'secret', 'dragon', 'football'
        ]
        
        pwd_lower = password.lower()
        
        # Check for exact matches
        if pwd_lower in common_words:
            return True
        
        # Check for words with leet speak substitutions
        normalized = pwd_lower
        for sub, char in self.SUBSTITUTIONS.items():
            normalized = normalized.replace(sub, char)
        
        if normalized in common_words:
            return True
        
        # Check for words embedded in password
        for word in common_words:
            if word in pwd_lower and len(word) >= 5:
                return True
        
        return False
    
    def _estimate_crack_time(self, entropy: float, length: int) -> str:
        """
        Estimate time to crack password using brute force
        
        Assumes 1 billion guesses per second (modern GPU)
        """
        if entropy == 0:
            return "instantly"
        
        # Number of possible combinations
        combinations = 2 ** entropy
        
        # Guesses per second (1 billion = modern GPU)
        guesses_per_sec = 1_000_000_000
        
        # Time in seconds
        seconds = combinations / guesses_per_sec / 2  # Divide by 2 for average case
        
        # Convert to human-readable
        if seconds < 1:
            return "instantly"
        elif seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.1f} minutes"
        elif seconds < 86400:
            return f"{seconds/3600:.1f} hours"
        elif seconds < 31536000:
            return f"{seconds/86400:.1f} days"
        elif seconds < 31536000 * 100:
            return f"{seconds/31536000:.1f} years"
        elif seconds < 31536000 * 1000:
            return f"{seconds/31536000:.0f} years"
        elif seconds < 31536000 * 1000000:
            return f"{seconds/(31536000*1000):.0f} thousand years"
        else:
            return f"{seconds/(31536000*1000000):.0f} million years"
    
    def batch_analyze(self, passwords: List[str]) -> List[PasswordAnalysis]:
        """Analyze multiple passwords"""
        return [self.analyze(pwd) for pwd in passwords]
    
    def get_stats(self) -> Dict:
        """Get analyzer statistics"""
        return {
            'total_analyzed': self.total_analyzed,
            'weak_count': self.weak_count,
            'strong_count': self.strong_count,
            'weak_percentage': (self.weak_count / self.total_analyzed * 100) if self.total_analyzed > 0 else 0
        }


def analyze_password(password: str) -> Dict:
    """
    Convenience function for single password analysis
    
    Args:
        password: Password to analyze
        
    Returns:
        Dict with analysis results
    """
    analyzer = PasswordStrengthAnalyzer()
    result = analyzer.analyze(password)
    
    return {
        'score': result.score,
        'strength': result.strength,
        'entropy': result.entropy,
        'issues': result.issues,
        'suggestions': result.suggestions,
        'crack_time': result.crack_time
    }


if __name__ == "__main__":
    # Demo usage
    print("="*60)
    print("PASSWORD STRENGTH ANALYZER - Demo")
    print("="*60)
    
    test_passwords = [
        "password123",           # Weak
        "P@ssw0rd",             # Medium  
        "MyS3cur3P@ss!",        # Strong
        "xK9#mP2$vL8@nQ4&zR7"  # Very Strong
    ]
    
    analyzer = PasswordStrengthAnalyzer()
    
    for pwd in test_passwords:
        print(f"\nPassword: {pwd}")
        result = analyzer.analyze(pwd)
        print(f"  Score: {result.score}/100")
        print(f"  Strength: {result.strength.upper()}")
        print(f"  Entropy: {result.entropy:.1f} bits")
        print(f"  Crack Time: {result.crack_time}")
        if result.issues:
            print(f"  Issues: {', '.join(result.issues)}")
        if result.suggestions:
            print(f"  Suggestions: {result.suggestions[0]}")
    
    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    stats = analyzer.get_stats()
    print(f"Total analyzed: {stats['total_analyzed']}")
    print(f"Weak passwords: {stats['weak_count']} ({stats['weak_percentage']:.1f}%)")
    print(f"Strong passwords: {stats['strong_count']}")
