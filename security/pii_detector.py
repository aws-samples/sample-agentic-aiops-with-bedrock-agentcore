"""PII Detection and Redaction Module"""
import re

PII_PATTERNS = {
    'email': (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
    'ssn': (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),
    'phone': (r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b', '[PHONE]'),
    'credit_card': (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[CREDIT_CARD]'),
    'ip_address': (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP_ADDRESS]'),
    'aws_key': (r'(?:AKIA|ASIA)[0-9A-Z]{16}', '[AWS_KEY]'),
    'name': (r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[NAME]')
}

def detect_pii(text: str) -> dict:
    """Detect PII in text and return findings"""
    findings = {}
    for pii_type, (pattern, _) in PII_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            findings[pii_type] = len(matches) if isinstance(matches[0], str) else len(matches)
    return findings

def redact_pii(text: str) -> str:
    """Redact PII from text"""
    redacted = text
    for pii_type, (pattern, replacement) in PII_PATTERNS.items():
        redacted = re.sub(pattern, replacement, redacted)
    return redacted

def sanitize_incident_data(incident_data: dict) -> dict:
    """Sanitize incident data by redacting PII"""
    sanitized = incident_data.copy()
    text_fields = ['description', 'short_description', 'work_notes', 'close_notes']
    
    for field in text_fields:
        if field in sanitized and sanitized[field]:
            sanitized[field] = redact_pii(str(sanitized[field]))
    
    return sanitized
