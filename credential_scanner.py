#!/usr/bin/env python3
"""
Credential Scanner for Agent Builders
Scans workspace for common credential storage vulnerabilities

Usage:
    python3 credential_scanner.py /path/to/workspace

Reports:
- Plaintext credentials in files
- Hardcoded API keys in source
- Insecure file permissions
- Credentials in Git history
- Environment variables in scripts

Author: Sparky-Sentry-1065
License: MIT
"""

import os
import re
import sys
import stat
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

# Patterns for credential detection
CREDENTIAL_PATTERNS = {
    'openai_key': r'sk-[a-zA-Z0-9]{48,}',
    'anthropic_key': r'sk-ant-[a-zA-Z0-9\-]{95,}',
    'aws_key': r'AKIA[0-9A-Z]{16}',
    'private_key': r'-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----',
    'jwt': r'eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}',
    'generic_key': r'(api[_-]?key|secret[_-]?key|password|token)\s*[:=]\s*["\']([^"\']{16,})["\']',
    'solana_key': r'[1-9A-HJ-NP-Za-km-z]{32,44}',  # Base58
}

def scan_file_content(filepath: Path) -> List[Tuple[str, int, str, str]]:
    """
    Scan file content for credential patterns.
    Returns: [(pattern_name, line_number, matched_text, context)]
    """
    findings = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for pattern_name, pattern in CREDENTIAL_PATTERNS.items():
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        # Redact matched credential
                        matched = match.group(0)
                        if len(matched) > 8:
                            redacted = matched[:4] + '*' * (len(matched) - 8) + matched[-4:]
                        else:
                            redacted = '*' * len(matched)
                        
                        findings.append((
                            pattern_name,
                            line_num,
                            redacted,
                            line.strip()[:80]  # Context (first 80 chars)
                        ))
    except Exception as e:
        pass  # Skip unreadable files
    
    return findings

def check_file_permissions(filepath: Path) -> Dict[str, any]:
    """Check if file has insecure permissions."""
    st = os.stat(filepath)
    mode = stat.filemode(st.st_mode)
    
    # Check if readable by group or others
    readable_by_others = bool(st.st_mode & stat.S_IROTH)
    readable_by_group = bool(st.st_mode & stat.S_IRGRP)
    
    return {
        'mode': mode,
        'insecure': readable_by_others or readable_by_group,
        'owner_only': not (readable_by_others or readable_by_group)
    }

def scan_git_history(repo_path: Path) -> List[str]:
    """
    Scan Git history for credential patterns.
    Returns list of commits with potential credentials.
    """
    findings = []
    
    if not (repo_path / '.git').exists():
        return findings
    
    try:
        # Search git log for credential patterns
        for pattern_name, pattern in CREDENTIAL_PATTERNS.items():
            result = subprocess.run(
                ['git', 'log', '-p', '-S', pattern, '--all'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                commits = re.findall(r'commit ([a-f0-9]{40})', result.stdout)
                for commit in commits[:5]:  # Limit to 5 most recent
                    findings.append(f"{pattern_name} found in commit {commit[:8]}")
    except Exception:
        pass
    
    return findings

def scan_workspace(workspace_path: Path) -> Dict:
    """Scan entire workspace for vulnerabilities."""
    
    results = {
        'credential_files': [],
        'insecure_permissions': [],
        'git_history': [],
        'summary': {
            'total_files_scanned': 0,
            'files_with_credentials': 0,
            'insecure_files': 0,
            'git_commits_flagged': 0
        }
    }
    
    # File extensions to scan
    extensions = {'.py', '.js', '.ts', '.json', '.yaml', '.yml', '.env', '.sh', '.bash', '.config'}
    
    print(f"[*] Scanning workspace: {workspace_path}")
    print(f"[*] Looking for credentials in: {', '.join(extensions)}")
    print()
    
    for root, dirs, files in os.walk(workspace_path):
        # Skip common non-source directories
        dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', 'venv', '.venv'}]
        
        for filename in files:
            filepath = Path(root) / filename
            
            # Skip if not target extension
            if filepath.suffix not in extensions:
                continue
            
            results['summary']['total_files_scanned'] += 1
            
            # Scan content
            findings = scan_file_content(filepath)
            if findings:
                results['summary']['files_with_credentials'] += 1
                results['credential_files'].append({
                    'file': str(filepath.relative_to(workspace_path)),
                    'findings': findings
                })
            
            # Check permissions
            perms = check_file_permissions(filepath)
            if perms['insecure']:
                results['summary']['insecure_files'] += 1
                results['insecure_permissions'].append({
                    'file': str(filepath.relative_to(workspace_path)),
                    'mode': perms['mode']
                })
    
    # Scan Git history
    git_findings = scan_git_history(workspace_path)
    results['git_history'] = git_findings
    results['summary']['git_commits_flagged'] = len(git_findings)
    
    return results

def print_report(results: Dict):
    """Print human-readable security report."""
    
    print("=" * 80)
    print("CREDENTIAL SECURITY SCAN REPORT")
    print("=" * 80)
    print()
    
    summary = results['summary']
    print(f"Files scanned: {summary['total_files_scanned']}")
    print(f"Files with credentials: {summary['files_with_credentials']}")
    print(f"Files with insecure permissions: {summary['insecure_files']}")
    print(f"Git commits flagged: {summary['git_commits_flagged']}")
    print()
    
    if results['credential_files']:
        print("=" * 80)
        print("CREDENTIALS FOUND IN FILES")
        print("=" * 80)
        for item in results['credential_files']:
            print(f"\n📁 {item['file']}")
            for pattern, line_num, redacted, context in item['findings']:
                print(f"  Line {line_num}: {pattern}")
                print(f"    Found: {redacted}")
                print(f"    Context: {context}")
        print()
    
    if results['insecure_permissions']:
        print("=" * 80)
        print("INSECURE FILE PERMISSIONS")
        print("=" * 80)
        for item in results['insecure_permissions']:
            print(f"\n📄 {item['file']}")
            print(f"  Permissions: {item['mode']}")
            print(f"  ❌ Readable by group or others")
            print(f"  Fix: chmod 600 {item['file']}")
        print()
    
    if results['git_history']:
        print("=" * 80)
        print("CREDENTIALS IN GIT HISTORY")
        print("=" * 80)
        for finding in results['git_history']:
            print(f"  ⚠️  {finding}")
        print()
        print("  WARNING: Credentials in Git history persist even after deletion.")
        print("  Recommendation: Revoke these credentials and rotate to new ones.")
        print()
    
    # Risk assessment
    total_issues = (
        summary['files_with_credentials'] +
        summary['insecure_files'] +
        summary['git_commits_flagged']
    )
    
    print("=" * 80)
    print("RISK ASSESSMENT")
    print("=" * 80)
    if total_issues == 0:
        print("✅ No critical issues found. Workspace appears secure.")
    elif total_issues <= 3:
        print("⚠️  LOW RISK: Some issues found. Review and remediate.")
    elif total_issues <= 10:
        print("⚠️  MEDIUM RISK: Multiple vulnerabilities detected. Prioritize fixes.")
    else:
        print("🚨 HIGH RISK: Significant security issues. Immediate action required.")
    
    print()
    print("For detailed remediation guidance, see:")
    print("https://github.com/therealsparky1/sparky-sentinel/blob/main/CREDENTIAL_STORAGE_REPORT.md")
    print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 credential_scanner.py <workspace_path>")
        print()
        print("Example:")
        print("  python3 credential_scanner.py /root/.openclaw/workspace")
        sys.exit(1)
    
    workspace = Path(sys.argv[1])
    
    if not workspace.exists():
        print(f"Error: Workspace not found: {workspace}")
        sys.exit(1)
    
    results = scan_workspace(workspace)
    print_report(results)
