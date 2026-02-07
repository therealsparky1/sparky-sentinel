#!/usr/bin/env python3
"""
XSS (Cross-Site Scripting) Detector
Production-ready security tool for detecting XSS attack vectors
"""

import re
import html
from typing import List, Dict
from dataclasses import dataclass
from enum import Enum


class XSSType(Enum):
    """Types of XSS attacks"""
    REFLECTED = "reflected"
    STORED = "stored"
    DOM_BASED = "dom_based"
    UNKNOWN = "unknown"


@dataclass
class XSSAnalysis:
    """Results of XSS analysis"""
    is_threat: bool
    xss_type: XSSType
    risk_score: int  # 0-100
    detected_vectors: List[str]
    sanitized_output: str
    issues: List[str]
    recommendations: List[str]


class XSSDetector:
    """Detect XSS (Cross-Site Scripting) attack vectors"""
    
    # Dangerous HTML tags
    DANGEROUS_TAGS = [
        'script', 'iframe', 'object', 'embed', 'applet',
        'meta', 'link', 'style', 'base', 'form'
    ]
    
    # Dangerous attributes
    DANGEROUS_ATTRIBUTES = [
        'onclick', 'onload', 'onerror', 'onmouseover',
        'onmouseout', 'onfocus', 'onblur', 'onchange',
        'onsubmit', 'onkeyup', 'onkeydown', 'onkeypress'
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        # Script tags
        (r'<\s*script[^>]*>', 'Script tag injection'),
        (r'javascript\s*:', 'JavaScript protocol'),
        (r'vbscript\s*:', 'VBScript protocol'),
        
        # Event handlers
        (r'on\w+\s*=', 'Event handler injection'),
        
        # Iframe injection
        (r'<\s*iframe[^>]*>', 'Iframe injection'),
        
        # Object/embed tags
        (r'<\s*(object|embed|applet)[^>]*>', 'Object/Embed injection'),
        
        # Meta redirect
        (r'<\s*meta[^>]*http-equiv', 'Meta redirect injection'),
        
        # SVG with script
        (r'<\s*svg[^>]*>.*<\s*script', 'SVG script injection'),
        
        # Data URIs with script
        (r'data:text/html[^,]*,', 'Data URI injection'),
        
        # Expression (IE)
        (r'expression\s*\(', 'CSS expression injection (IE)'),
        
        # Import
        (r'@import', 'CSS @import injection'),
        
        # Base64 encoded
        (r'base64\s*,', 'Base64 encoded content'),
        
        # Common bypasses
        (r'&#\d+;', 'HTML entity encoding (potential bypass)'),
        (r'\\u[0-9a-fA-F]{4}', 'Unicode escape (potential bypass)'),
        (r'\\x[0-9a-fA-F]{2}', 'Hex escape (potential bypass)'),
        
        # String concatenation
        (r'\+\s*[\'"]', 'String concatenation (potential bypass)'),
        
        # Comment-based obfuscation
        (r'<!--.*-->', 'HTML comment (potential obfuscation)'),
    ]
    
    def __init__(self):
        self.total_analyzed = 0
        self.threats_detected = 0
        self.high_risk_count = 0
    
    def analyze(self, user_input: str, context: str = "html") -> XSSAnalysis:
        """
        Analyze user input for XSS vectors
        
        Args:
            user_input: User-provided input to analyze
            context: Where the input will be used (html, attribute, javascript, url)
            
        Returns:
            XSSAnalysis with threat assessment
        """
        self.total_analyzed += 1
        
        detected_vectors = []
        issues = []
        recommendations = []
        risk_score = 0
        
        if not user_input:
            return self._create_safe_result("")
        
        input_lower = user_input.lower()
        
        # Check for dangerous tags
        for tag in self.DANGEROUS_TAGS:
            pattern = f'<\\s*{tag}[^>]*>'
            if re.search(pattern, input_lower):
                detected_vectors.append(f'{tag.upper()} tag detected')
                issues.append(f"Dangerous HTML tag: <{tag}>")
                risk_score += 20
        
        # Check for dangerous attributes
        for attr in self.DANGEROUS_ATTRIBUTES:
            if attr in input_lower:
                detected_vectors.append(f'{attr} event handler')
                issues.append(f"Event handler detected: {attr}")
                risk_score += 15
        
        # Check XSS patterns
        for pattern, description in self.XSS_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE | re.DOTALL):
                detected_vectors.append(description)
                risk_score += 10
        
        # Check for encoded attacks
        if self._has_encoding_bypass(user_input):
            detected_vectors.append('Encoding bypass attempt')
            issues.append("Detected encoding that may bypass filters")
            risk_score += 15
        
        # Check for broken HTML (potential bypass)
        if '<' in user_input and '>' in user_input:
            if not self._is_valid_html(user_input):
                detected_vectors.append('Malformed HTML')
                risk_score += 10
        
        # Context-specific checks
        if context == "attribute":
            if '"' in user_input or "'" in user_input:
                detected_vectors.append('Quote in attribute context')
                issues.append("Quotes can break out of attribute context")
                risk_score += 15
        
        elif context == "javascript":
            if any(char in user_input for char in ['<', '>', '"', "'", '\\']):
                detected_vectors.append('Special chars in JS context')
                issues.append("Special characters in JavaScript context")
                risk_score += 20
        
        elif context == "url":
            if re.search(r'javascript:|data:|vbscript:', input_lower):
                detected_vectors.append('Dangerous URL protocol')
                issues.append("Dangerous protocol in URL context")
                risk_score += 25
        
        # Check input length
        if len(user_input) > 1000:
            issues.append(f"Unusually long input ({len(user_input)} chars)")
            risk_score += 5
        
        # Determine threat level
        risk_score = min(100, risk_score)
        is_threat = risk_score >= 20
        
        if is_threat:
            self.threats_detected += 1
        
        if risk_score >= 60:
            self.high_risk_count += 1
        
        # Determine XSS type (simplified)
        xss_type = self._determine_xss_type(detected_vectors)
        
        # Generate recommendations
        if is_threat:
            recommendations.append("Apply context-appropriate output encoding")
            recommendations.append("Use Content Security Policy (CSP) headers")
            recommendations.append("Validate and sanitize all user input")
            
            if context == "html":
                recommendations.append("HTML-encode output: < > & \" '")
            elif context == "attribute":
                recommendations.append("Attribute-encode output and use quotes")
            elif context == "javascript":
                recommendations.append("JavaScript-encode output")
            elif context == "url":
                recommendations.append("URL-encode output and validate protocol")
            
            if risk_score >= 60:
                recommendations.append("REJECT this input and log the attempt")
        
        # Sanitize output
        sanitized = self._sanitize_output(user_input, context)
        
        return XSSAnalysis(
            is_threat=is_threat,
            xss_type=xss_type,
            risk_score=risk_score,
            detected_vectors=detected_vectors,
            sanitized_output=sanitized,
            issues=issues,
            recommendations=recommendations
        )
    
    def _has_encoding_bypass(self, user_input: str) -> bool:
        """Check for encoding bypass attempts"""
        # HTML entities
        if re.search(r'&#x?[0-9a-fA-F]+;', user_input):
            return True
        
        # URL encoding
        if re.search(r'%[0-9a-fA-F]{2}', user_input):
            return True
        
        # Unicode escapes
        if re.search(r'\\u[0-9a-fA-F]{4}', user_input):
            return True
        
        # Hex escapes
        if re.search(r'\\x[0-9a-fA-F]{2}', user_input):
            return True
        
        return False
    
    def _is_valid_html(self, text: str) -> bool:
        """Basic check for valid HTML structure"""
        # Count opening and closing brackets
        open_count = text.count('<')
        close_count = text.count('>')
        
        # Valid HTML should have balanced brackets
        return abs(open_count - close_count) <= 1
    
    def _determine_xss_type(self, vectors: List[str]) -> XSSType:
        """Determine XSS type based on detected vectors"""
        # Simplified classification
        if any('script' in v.lower() for v in vectors):
            return XSSType.REFLECTED
        elif any('event' in v.lower() for v in vectors):
            return XSSType.REFLECTED
        elif any('dom' in v.lower() or 'data uri' in v.lower() for v in vectors):
            return XSSType.DOM_BASED
        elif vectors:
            return XSSType.REFLECTED
        else:
            return XSSType.UNKNOWN
    
    def _sanitize_output(self, user_input: str, context: str) -> str:
        """
        Sanitize output based on context
        
        Note: In production, use framework-provided sanitization!
        """
        if context == "html":
            # HTML encode
            return html.escape(user_input, quote=True)
        
        elif context == "attribute":
            # HTML encode + ensure quotes
            return html.escape(user_input, quote=True)
        
        elif context == "javascript":
            # Escape for JavaScript context
            sanitized = user_input.replace('\\', '\\\\')
            sanitized = sanitized.replace('"', '\\"')
            sanitized = sanitized.replace("'", "\\'")
            sanitized = sanitized.replace('<', '\\x3C')
            sanitized = sanitized.replace('>', '\\x3E')
            return sanitized
        
        elif context == "url":
            # Basic URL encoding (use urllib.parse.quote in production)
            import urllib.parse
            return urllib.parse.quote(user_input, safe='')
        
        else:
            return html.escape(user_input, quote=True)
    
    def _create_safe_result(self, user_input: str) -> XSSAnalysis:
        """Create result for safe input"""
        return XSSAnalysis(
            is_threat=False,
            xss_type=XSSType.UNKNOWN,
            risk_score=0,
            detected_vectors=[],
            sanitized_output=user_input,
            issues=[],
            recommendations=[]
        )
    
    def is_safe(self, user_input: str, context: str = "html") -> bool:
        """Quick safety check"""
        result = self.analyze(user_input, context)
        return not result.is_threat
    
    def get_stats(self) -> Dict:
        """Get detector statistics"""
        return {
            'total_analyzed': self.total_analyzed,
            'threats_detected': self.threats_detected,
            'high_risk_count': self.high_risk_count,
            'threat_rate': (self.threats_detected / self.total_analyzed * 100) if self.total_analyzed > 0 else 0
        }


def detect_xss(user_input: str, context: str = "html") -> Dict:
    """
    Convenience function for XSS detection
    
    Args:
        user_input: User-provided input
        context: Output context (html, attribute, javascript, url)
        
    Returns:
        Dict with analysis results
    """
    detector = XSSDetector()
    result = detector.analyze(user_input, context)
    
    return {
        'is_threat': result.is_threat,
        'xss_type': result.xss_type.value,
        'risk_score': result.risk_score,
        'detected_vectors': result.detected_vectors,
        'sanitized_output': result.sanitized_output,
        'issues': result.issues,
        'recommendations': result.recommendations
    }


if __name__ == "__main__":
    # Demo usage
    print("="*60)
    print("XSS DETECTOR - Demo")
    print("="*60)
    
    test_inputs = {
        "Normal Text": "Hello World",
        "Script Tag": "<script>alert('XSS')</script>",
        "Event Handler": "<img src=x onerror=alert('XSS')>",
        "JavaScript Protocol": "<a href=\"javascript:alert('XSS')\">Click</a>",
        "SVG Injection": "<svg onload=alert('XSS')>",
        "Encoded": "&#60;script&#62;alert('XSS')&#60;/script&#62;",
    }
    
    detector = XSSDetector()
    
    for name, input_str in test_inputs.items():
        print(f"\n{name}: {input_str[:50]}...")
        result = detector.analyze(input_str)
        print(f"  Threat: {result.is_threat}")
        print(f"  Risk Score: {result.risk_score}/100")
        if result.detected_vectors:
            print(f"  Vectors: {', '.join(result.detected_vectors[:2])}")
        if result.issues:
            print(f"  Issue: {result.issues[0]}")
        if result.recommendations:
            print(f"  Recommendation: {result.recommendations[0]}")
        print(f"  Sanitized: {result.sanitized_output[:50]}...")
    
    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    stats = detector.get_stats()
    print(f"Total analyzed: {stats['total_analyzed']}")
    print(f"Threats detected: {stats['threats_detected']} ({stats['threat_rate']:.1f}%)")
    print(f"High risk: {stats['high_risk_count']}")
