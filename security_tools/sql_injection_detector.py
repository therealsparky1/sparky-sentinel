#!/usr/bin/env python3
"""
SQL Injection Detector
Production-ready security tool for detecting SQL injection attempts
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class ThreatLevel(Enum):
    """SQL injection threat severity"""
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"
    CRITICAL = "critical"


@dataclass
class SQLInjectionAnalysis:
    """Results of SQL injection analysis"""
    threat_level: ThreatLevel
    risk_score: int  # 0-100
    detected_patterns: List[str]
    sanitized_input: str
    issues: List[str]
    recommendations: List[str]


class SQLInjectionDetector:
    """Detect SQL injection attempts in user input"""
    
    # SQL keywords that shouldn't appear in normal input
    SQL_KEYWORDS = [
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
        'ALTER', 'EXEC', 'EXECUTE', 'UNION', 'CONCAT', 'CHAR',
        'INFORMATION_SCHEMA', 'SYSOBJECTS', 'SYSCOLUMNS'
    ]
    
    # Dangerous SQL patterns
    DANGEROUS_PATTERNS = [
        # Comment injection
        (r'(--|#|/\*|\*/)', 'SQL comment injection'),
        
        # Union-based injection
        (r'\bUNION\s+(ALL\s+)?SELECT\b', 'UNION SELECT injection'),
        
        # Boolean-based blind injection
        (r"(\bOR\b\s+\d+\s*=\s*\d+|\bAND\b\s+\d+\s*=\s*\d+)", 'Boolean-based injection'),
        (r"'\s*(OR|AND)\s+'?\w+'\s*=\s*'\w+", 'Quote-based boolean injection'),
        
        # Time-based blind injection
        (r'\b(SLEEP|WAITFOR|BENCHMARK)\s*\(', 'Time-based blind injection'),
        
        # Stacked queries
        (r';\s*(SELECT|INSERT|UPDATE|DELETE|DROP)', 'Stacked query injection'),
        
        # Database fingerprinting
        (r'\b(@@version|version\(\)|user\(\))\b', 'Database fingerprinting'),
        
        # File operations
        (r'\b(LOAD_FILE|INTO\s+OUTFILE|INTO\s+DUMPFILE)\b', 'File operation injection'),
        
        # Hex/char encoding
        (r'0x[0-9a-fA-F]+', 'Hexadecimal encoding (potential obfuscation)'),
        (r'\bCHAR\s*\(\s*\d+', 'CHAR encoding (potential obfuscation)'),
        
        # Quote escaping attempts
        (r"(\\'+|''+|`+)", 'Quote escaping attempt'),
        
        # Always-true conditions
        (r"('\s*OR\s*'1'\s*=\s*'1|\bOR\b\s+1\s*=\s*1)", 'Always-true condition'),
        
        # Batched statements
        (r';\s*--', 'Batched statement with comment'),
        
        # XPath injection (in SQL context)
        (r'\bEXTRACTVALUE\s*\(', 'XPath injection attempt'),
    ]
    
    # Suspicious patterns (lower severity)
    SUSPICIOUS_PATTERNS = [
        (r"['\"]", 'Unescaped quotes'),
        (r'\b(SELECT|INSERT|UPDATE|DELETE)\b', 'SQL keywords present'),
        (r'[;<>]', 'Special SQL characters'),
        (r'\bFROM\b', 'FROM keyword'),
        (r'\bWHERE\b', 'WHERE keyword'),
    ]
    
    def __init__(self):
        self.total_analyzed = 0
        self.threats_detected = 0
        self.critical_threats = 0
    
    def analyze(self, user_input: str, field_name: str = "input") -> SQLInjectionAnalysis:
        """
        Analyze user input for SQL injection attempts
        
        Args:
            user_input: User-provided input to analyze
            field_name: Name of the input field (for context)
            
        Returns:
            SQLInjectionAnalysis with threat assessment
        """
        self.total_analyzed += 1
        
        detected_patterns = []
        issues = []
        recommendations = []
        risk_score = 0
        
        if not user_input:
            return SQLInjectionAnalysis(
                threat_level=ThreatLevel.SAFE,
                risk_score=0,
                detected_patterns=[],
                sanitized_input="",
                issues=[],
                recommendations=[]
            )
        
        input_upper = user_input.upper()
        
        # Check dangerous patterns
        for pattern, description in self.DANGEROUS_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                detected_patterns.append(description)
                issues.append(f"Detected: {description}")
                risk_score += 25
        
        # Check suspicious patterns
        for pattern, description in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                if description not in detected_patterns:
                    detected_patterns.append(description)
                risk_score += 5
        
        # Check for multiple SQL keywords
        keyword_count = sum(1 for kw in self.SQL_KEYWORDS if kw in input_upper)
        if keyword_count >= 3:
            issues.append(f"Multiple SQL keywords detected ({keyword_count})")
            risk_score += 20
        elif keyword_count >= 1:
            risk_score += 10
        
        # Check input length (very long inputs can indicate injection)
        if len(user_input) > 500:
            issues.append(f"Unusually long input ({len(user_input)} chars)")
            risk_score += 10
        
        # Check for encoded characters (URL/hex encoding)
        if re.search(r'%[0-9a-fA-F]{2}', user_input):
            issues.append("URL-encoded characters detected")
            risk_score += 15
        
        # Determine threat level
        risk_score = min(100, risk_score)
        
        if risk_score >= 75:
            threat_level = ThreatLevel.CRITICAL
            self.critical_threats += 1
            self.threats_detected += 1
        elif risk_score >= 50:
            threat_level = ThreatLevel.DANGEROUS
            self.threats_detected += 1
        elif risk_score >= 25:
            threat_level = ThreatLevel.SUSPICIOUS
        else:
            threat_level = ThreatLevel.SAFE
        
        # Generate recommendations
        if threat_level != ThreatLevel.SAFE:
            recommendations.append("Use parameterized queries (prepared statements)")
            recommendations.append("Implement input validation and sanitization")
            recommendations.append("Apply principle of least privilege for database access")
            
            if any('quote' in p.lower() for p in detected_patterns):
                recommendations.append("Escape all user input before SQL concatenation")
            
            if any('union' in p.lower() for p in detected_patterns):
                recommendations.append("Block UNION statements in user input")
            
            if risk_score >= 75:
                recommendations.append("REJECT this input immediately and log the attempt")
                recommendations.append("Consider rate-limiting or blocking this source")
        
        # Sanitize input (basic sanitization for demonstration)
        sanitized = self._sanitize_input(user_input)
        
        return SQLInjectionAnalysis(
            threat_level=threat_level,
            risk_score=risk_score,
            detected_patterns=detected_patterns,
            sanitized_input=sanitized,
            issues=issues,
            recommendations=recommendations
        )
    
    def _sanitize_input(self, user_input: str) -> str:
        """
        Basic input sanitization (for demonstration)
        
        In production, use parameterized queries instead!
        """
        # Remove SQL comments
        sanitized = re.sub(r'(--|#|/\*|\*/)', '', user_input)
        
        # Escape single quotes
        sanitized = sanitized.replace("'", "''")
        
        # Remove semicolons (prevent stacked queries)
        sanitized = sanitized.replace(';', '')
        
        # Remove common SQL keywords
        for keyword in ['UNION', 'SELECT', 'DROP', 'DELETE', 'INSERT', 'UPDATE']:
            sanitized = re.sub(keyword, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    def batch_analyze(self, inputs: Dict[str, str]) -> Dict[str, SQLInjectionAnalysis]:
        """
        Analyze multiple inputs
        
        Args:
            inputs: Dict of {field_name: user_input}
            
        Returns:
            Dict of {field_name: analysis}
        """
        return {
            field: self.analyze(value, field)
            for field, value in inputs.items()
        }
    
    def is_safe(self, user_input: str) -> bool:
        """Quick safety check"""
        result = self.analyze(user_input)
        return result.threat_level == ThreatLevel.SAFE
    
    def get_stats(self) -> Dict:
        """Get detector statistics"""
        return {
            'total_analyzed': self.total_analyzed,
            'threats_detected': self.threats_detected,
            'critical_threats': self.critical_threats,
            'threat_rate': (self.threats_detected / self.total_analyzed * 100) if self.total_analyzed > 0 else 0
        }


def detect_sql_injection(user_input: str) -> Dict:
    """
    Convenience function for SQL injection detection
    
    Args:
        user_input: User-provided input to analyze
        
    Returns:
        Dict with analysis results
    """
    detector = SQLInjectionDetector()
    result = detector.analyze(user_input)
    
    return {
        'threat_level': result.threat_level.value,
        'risk_score': result.risk_score,
        'detected_patterns': result.detected_patterns,
        'sanitized_input': result.sanitized_input,
        'issues': result.issues,
        'recommendations': result.recommendations
    }


if __name__ == "__main__":
    # Demo usage
    print("="*60)
    print("SQL INJECTION DETECTOR - Demo")
    print("="*60)
    
    test_inputs = {
        "Normal Input": "John Doe",
        "Email": "user@example.com",
        "Union Injection": "' UNION SELECT password FROM users--",
        "Boolean Injection": "admin' OR '1'='1",
        "Comment Injection": "test'; DROP TABLE users--",
        "Time-based": "1' AND SLEEP(5)--",
    }
    
    detector = SQLInjectionDetector()
    
    for name, input_str in test_inputs.items():
        print(f"\n{name}: {input_str}")
        result = detector.analyze(input_str)
        print(f"  Threat Level: {result.threat_level.value.upper()}")
        print(f"  Risk Score: {result.risk_score}/100")
        if result.detected_patterns:
            print(f"  Detected: {', '.join(result.detected_patterns[:2])}")
        if result.issues:
            print(f"  Issues: {result.issues[0]}")
        if result.recommendations:
            print(f"  Recommendation: {result.recommendations[0]}")
        print(f"  Sanitized: {result.sanitized_input}")
    
    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    stats = detector.get_stats()
    print(f"Total analyzed: {stats['total_analyzed']}")
    print(f"Threats detected: {stats['threats_detected']} ({stats['threat_rate']:.1f}%)")
    print(f"Critical threats: {stats['critical_threats']}")
