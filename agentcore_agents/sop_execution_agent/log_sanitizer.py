"""Log sanitization to prevent credential and PII exposure"""
import re

def sanitize_log(message: str) -> str:
    """Remove sensitive data from log messages"""
    # IP addresses
    message = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '<IP_REDACTED>', message)
    # Passwords
    message = re.sub(r'password["\s:=]+[^\s"]+', 'password=<REDACTED>', message, flags=re.IGNORECASE)
    # API keys/tokens
    message = re.sub(r'(api[_-]?key|token|secret)["\s:=]+[^\s"]+', r'\1=<REDACTED>', message, flags=re.IGNORECASE)
    # AWS credentials
    message = re.sub(r'AKIA[0-9A-Z]{16}', '<AWS_KEY_REDACTED>', message)
    # Base64 encoded (potential credentials)
    message = re.sub(r'Basic [A-Za-z0-9+/=]{20,}', 'Basic <REDACTED>', message)
    message = re.sub(r'Bearer [A-Za-z0-9\-._~+/]+=*', 'Bearer <REDACTED>', message)
    return message
