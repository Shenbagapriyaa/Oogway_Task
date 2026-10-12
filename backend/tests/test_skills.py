import pytest
from app.skills.ship30_writer import generate_source_brief
from app.services.ingestion_service import ingestion_service

def test_ship30_fallback_is_a_grounded_brief():
    sample_chunk = [{
        "guest": "Elena Verna",
        "title": "Elena Verna 4.0",
        "timestamp": "00:03:15",
        "quote": "Product-market fit is no longer a milestone, you have to recapture it every three months."
    }]
    essay = generate_source_brief("recapturing product market fit", sample_chunk)

    assert "# Essay brief:" in essay
    assert "Elena Verna" in essay
    assert "Product-market fit is no longer a milestone" in essay
    assert "not a 1,250-word essay" in essay
    assert "70/30 innovation ratio" not in essay
