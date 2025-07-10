#!/usr/bin/env python3
"""
Claude Secrets Detector Hook
Detects potential secrets, API keys, and credentials in code
"""

import json
import sys
import re

# Common patterns for secrets detection
SECRET_PATTERNS = {
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "aws_secret_key": r"(?i)aws(.{0,20})?(?-i)['\"][0-9a-zA-Z/+=]{40}['\"]",
    "github_token": r"gh[ps]_[0-9a-zA-Z]{36}",
    "private_key": r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
    "api_key_generic": r"(?i)(api[_-]?key|apikey|api_secret)[\s]*[:=][\s]*['\"][a-zA-Z0-9_\-]{20,}['\"]",
    "password_in_url": r"://[^:]+:[^@]+@",
    "jwt_token": r"eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*",
    "slack_token": r"xox[baprs]-[0-9a-zA-Z-]+",
    "google_api": r"AIza[0-9A-Za-z_-]{35}",
    "stripe_key": r"(sk|pk)_(test|live)_[0-9a-zA-Z]{24,}",
    "pypi_token": r"pypi-[0-9a-zA-Z_-]{40,}",
    "npm_token": r"npm_[0-9a-zA-Z]{36}",
    "basic_auth": r"(?i)basic\s+[a-zA-Z0-9+/]{20,}={0,2}",
    "bearer_token": r"(?i)bearer\s+[a-zA-Z0-9_\-\.]+",
    "mailgun_key": r"key-[0-9a-z]{32}",
    "twilio_key": r"SK[0-9a-f]{32}",
    "firebase_key": r"(?i)firebase.*['\"][0-9a-zA-Z_-]{30,}['\"]",
    "db_connection": r"(?i)(mongodb\+srv|postgresql|mysql|redis)://[^:]+:[^@]+@",
    "discord_token": r"[MN][a-zA-Z\d_-]{23,25}\.[a-zA-Z\d_-]{6}\.[a-zA-Z\d_-]{27}",
    "generic_secret": r"(?i)(secret|token|password|passwd|pwd)[\s]*[:=][\s]*['\"][^'\"]{8,}['\"]"
}

# Patterns that are likely false positives
FALSE_POSITIVE_PATTERNS = [
    r"(?i)example",
    r"(?i)sample",
    r"(?i)test",
    r"(?i)dummy",
    r"(?i)fake",
    r"(?i)mock",
    r"<[^>]+>",  # Placeholder like <your-api-key>
    r"\$\{[^}]+\}",  # Template variable ${API_KEY}
    r"xxx+",  # Redacted values
    r"\*{3,}",  # Asterisks
    r"your[_-]?api[_-]?key",
    r"TODO|FIXME",
    r"localhost|127\.0\.0\.1"
]

def is_likely_false_positive(match_text, surrounding_text):
    """Check if a match is likely a false positive"""
    # Check the match itself
    for pattern in FALSE_POSITIVE_PATTERNS:
        if re.search(pattern, match_text, re.IGNORECASE):
            return True
    
    # Check surrounding context
    for pattern in FALSE_POSITIVE_PATTERNS:
        if re.search(pattern, surrounding_text, re.IGNORECASE):
            return True
    
    # Check if it's in a comment or documentation
    if surrounding_text.strip().startswith(('#', '//', '/*', '*', '"""', "'''")):
        return True
    
    return False

def check_content(content, file_path=""):
    """Check content for potential secrets"""
    issues = []
    
    # Skip certain file types that often have false positives
    skip_extensions = ['.md', '.txt', '.rst', '.example', '.sample', '.test']
    if any(file_path.endswith(ext) for ext in skip_extensions):
        return issues
    
    lines = content.split('\n')
    
    for pattern_name, pattern in SECRET_PATTERNS.items():
        for i, line in enumerate(lines):
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('#'):
                continue
                
            matches = re.finditer(pattern, line)
            for match in matches:
                match_text = match.group(0)
                
                # Get surrounding context
                start = max(0, match.start() - 20)
                end = min(len(line), match.end() + 20)
                surrounding = line[start:end]
                
                # Check for false positives
                if is_likely_false_positive(match_text, surrounding):
                    continue
                
                issues.append({
                    "type": pattern_name,
                    "line": i + 1,
                    "match": match_text[:50] + "..." if len(match_text) > 50 else match_text,
                    "severity": "high" if pattern_name in ["private_key", "aws_secret_key"] else "medium"
                })
    
    return issues

def format_issues(issues, file_path):
    """Format issues for display"""
    if not issues:
        return None
    
    output = f"🚨 SECURITY WARNING: Potential secrets detected in {file_path}\n"
    
    # Group by severity
    high_severity = [i for i in issues if i["severity"] == "high"]
    medium_severity = [i for i in issues if i["severity"] == "medium"]
    
    if high_severity:
        output += "\nHIGH SEVERITY:\n"
        for issue in high_severity:
            output += f"  • Line {issue['line']}: {issue['type']} - {issue['match']}\n"
    
    if medium_severity:
        output += "\nMEDIUM SEVERITY:\n"
        for issue in medium_severity[:5]:  # Limit to first 5 to avoid spam
            output += f"  • Line {issue['line']}: {issue['type']} - {issue['match']}\n"
        if len(medium_severity) > 5:
            output += f"  • ... and {len(medium_severity) - 5} more\n"
    
    output += "\nRecommendations:\n"
    output += "  • Use environment variables for sensitive values\n"
    output += "  • Add secrets to .gitignore\n"
    output += "  • Consider using a secrets management service\n"
    output += "  • If these are false positives, consider using placeholders like '<your-api-key>'\n"
    
    return output

def main():
    if len(sys.argv) < 2:
        sys.exit(0)
    
    try:
        tool_data = json.loads(sys.argv[1])
        tool_name = tool_data.get("tool_name", "")
        
        # Only check on Write, Edit, and MultiEdit operations
        if tool_name not in ["Write", "Edit", "MultiEdit"]:
            sys.exit(0)
        
        tool_input = tool_data.get("tool_input", {})
        
        # Get content based on tool type
        content = None
        file_path = tool_input.get("file_path", "")
        
        if tool_name == "Write":
            content = tool_input.get("content", "")
        elif tool_name == "Edit":
            # For Edit, check the new_string
            content = tool_input.get("new_string", "")
        elif tool_name == "MultiEdit":
            # For MultiEdit, check all new_strings
            edits = tool_input.get("edits", [])
            content = "\n".join(edit.get("new_string", "") for edit in edits)
        
        if content and file_path:
            issues = check_content(content, file_path)
            if issues:
                output = format_issues(issues, file_path)
                if output:
                    print(output)
                    print("-" * 50)
    
    except Exception:
        # Fail silently to not disrupt workflow
        pass
    
    sys.exit(0)

if __name__ == "__main__":
    main()