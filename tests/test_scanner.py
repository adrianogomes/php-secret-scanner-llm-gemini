from pathlib import Path
from php_secret_scanner_llm.scanner import mask_value, sanitize_assignment_value, Finding

def test_mask_value():
    assert mask_value("123") == "****"
    assert mask_value("1234") == "****"
    assert mask_value("senha_ficticia") == "se****ia"

def test_sanitize_assignment_value():
    line = '$apiKey = "sk-123456789";'
    sanitized = sanitize_assignment_value(line)
    assert 'sk-123456789' not in sanitized
    assert 'sk****89' in sanitized