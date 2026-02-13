"""Enhanced prompt injection detection and input sanitization"""
import re

INJECTION_PATTERNS = [
    r'ignore\s+(previous|all|above|prior)\s+(instructions?|prompts?|commands?)',
    r'disregard\s+(previous|all|above|prior)',
    r'forget\s+(previous|all|above|everything)',
    r'you\s+are\s+now',
    r'act\s+as\s+(a\s+)?(?!incident|analysis|validation|sop)',
    r'system\s+prompt',
    r'new\s+(instructions?|role|task)',
    r'override\s+(instructions?|settings?)',
    r'(delete|terminate|destroy|remove)\s+all',
    r'(stop|shutdown|kill)\s+all',
    r'<script[^>]*>',
    r'eval\s*\(',
    r'exec\s*\(',
    r'__import__',
    r'subprocess\.',
    r'os\.system',
    r'\$\{.*\}',  # Variable injection
    r'\|\s*(rm|dd|mkfs)',  # Command injection
]

DESTRUCTIVE_KEYWORDS = [
    'delete all', 'terminate all', 'destroy all', 'remove all',
    'stop all', 'shutdown all', 'kill all', 'drop all'
]

def detect_prompt_injection(text: str) -> tuple[bool, str]:
    """Detect prompt injection attempts"""
    text_lower = text.lower()
    
    # Check destructive keywords
    for keyword in DESTRUCTIVE_KEYWORDS:
        if keyword in text_lower:
            return True, f"Destructive command detected: {keyword}"
    
    # Check injection patterns
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True, f"Prompt injection pattern: {pattern}"
    
    return False, ""

def sanitize_input(text: str) -> str:
    """Sanitize input by removing suspicious content"""
    # Remove script tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE|re.DOTALL)
    # Remove command injection attempts
    text = re.sub(r'[|;&`$]', '', text)
    # Limit length
    return text[:2000]
