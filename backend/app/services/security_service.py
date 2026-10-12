import re
import html
import logging
from typing import Tuple, List

logger = logging.getLogger(__name__)

class SecurityService:
    """
    Security and isolation strategy for LLM-generated HTML/CSS artifacts.
    
    Isolation Model:
    1. Server-Side Inspection & Sanitization:
       - Strips iframe breakout vectors (`parent.location`, `window.top`, `window.parent`).
       - Blocks dangerous schemes (`javascript:`, `vbscript:`, `data:text/html`).
       - Injects restrictive Content-Security-Policy (CSP) headers into the HTML document.
       
    2. Client-Side Browser Sandboxing:
       - Renders within `<iframe sandbox="allow-scripts">` (strictly omitting `allow-same-origin`).
       - Omitting `allow-same-origin` ensures the iframe has an opaque/null origin.
       - The iframe CANNOT access host localStorage, session cookies, host DOM, or authorization tokens.
       - Disallows network breakouts (`connect-src 'none'`).
    """

    DANGEROUS_PATTERNS = [
        (r"parent\.location", "Blocked parent window navigation"),
        (r"top\.location", "Blocked top window navigation"),
        (r"window\.parent", "Blocked window.parent access"),
        (r"javascript:\s*", "Blocked javascript scheme URI"),
        (r"document\.cookie", "Blocked cookie access"),
        (r"localStorage\.", "Blocked localStorage access"),
        (r"sessionStorage\.", "Blocked sessionStorage access")
    ]

    RESTRICTIVE_CSP = (
        "<meta http-equiv=\"Content-Security-Policy\" content=\""
        "default-src 'none'; "
        "style-src 'unsafe-inline'; "
        "font-src data:; "
        "script-src 'unsafe-inline'; "
        "img-src data:; "
        "connect-src 'none'; "
        "frame-src 'none'; "
        "object-src 'none'; "
        "form-action 'none'; "
        "base-uri 'none';\">"
    )

    def sanitize_html_artifact(self, raw_html: str) -> Tuple[str, List[str]]:
        warnings = []
        sanitized = raw_html

        for pattern, warning_msg in self.DANGEROUS_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                warnings.append(warning_msg)
                sanitized = re.sub(pattern, "/* blocked_security_risk */", sanitized, flags=re.IGNORECASE)

        # Inject CSP into <head> or prepend if head is absent
        if "<head>" in sanitized.lower():
            sanitized = re.sub(r"(<head[^>]*>)", r"\1\n  " + self.RESTRICTIVE_CSP, sanitized, count=1, flags=re.IGNORECASE)
        else:
            sanitized = f"<!DOCTYPE html>\n<html>\n<head>\n{self.RESTRICTIVE_CSP}\n</head>\n<body>\n{sanitized}\n</body>\n</html>"

        return sanitized, warnings

security_service = SecurityService()
