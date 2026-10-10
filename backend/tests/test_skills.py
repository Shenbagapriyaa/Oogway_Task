import pytest
from app.skills.ship30_writer import generate_fallback_ship30_essay
from app.services.ingestion_service import ingestion_service

def test_ship30_essay_structure():
    sample_chunk = [{
        "guest": "Elena Verna",
        "title": "Elena Verna 4.0",
        "timestamp": "00:03:15",
        "quote": "Product-market fit is no longer a milestone, you have to recapture it every three months."
    }]
    essay = generate_fallback_ship30_essay("recapturing product market fit", sample_chunk)

    # 1. Word count verification (~1,250 words)
    words = essay.split()
    word_count = len(words)
    assert 600 <= word_count <= 1500, f"Expected ~1,250 words, got {word_count}"

    # 2. Headline & Hook
    assert "# " in essay
    assert "Elena Verna" in essay

    # 3. 4 Actionable Pillars
    assert "### Pillar 1:" in essay
    assert "### Pillar 2:" in essay
    assert "### Pillar 3:" in essay
    assert "### Pillar 4:" in essay

    # 4. Selective Bold Emphasis
    assert "**" in essay

    # 5. The 24-Hour Takeaway
    assert "24-Hour" in essay
    assert "Pillar" in essay
