import pytest
from app.services.retrieval_service import retrieval_service

@pytest.fixture(autouse=True)
def init_retrieval():
    if not retrieval_service.is_initialized:
        retrieval_service.initialize()

def test_retrieval_elena_verna():
    query = "Elena Verna product market fit Lovable growth loops"
    chunks, citations = retrieval_service.search(query, top_k=3)
    assert len(chunks) > 0
    assert len(citations) > 0
    guests = [c.guest for c in citations]
    assert any("Elena" in g for g in guests)
    assert any("00:" in c.timestamp for c in citations)
    assert len(citations[0].quote) > 10


def test_product_market_fit_query_returns_distinct_guest_excerpts():
    chunks, citations = retrieval_service.search(
        "What did Elena Verna say about product-market fit?",
        top_k=4,
    )

    assert chunks
    assert citations
    assert all(citation.guest == "Elena Verna" for citation in citations)
    assert len({(citation.episode_title, citation.quote) for citation in citations}) == len(citations)
    assert any(
        citation.timestamp == "01:03:43" and "every three months" in citation.quote.lower()
        for citation in citations
    )

def test_retrieval_keith_rabois():
    query = "Keith Rabois barrels and ammo"
    chunks, citations = retrieval_service.search(query, top_k=3)
    assert len(chunks) > 0
    guests = [c.guest for c in citations]
    assert any("Keith" in g for g in guests)

def test_out_of_domain_query():
    query = "How to bake sourdough bread with yeast and rye flour in a Dutch oven"
    chunks, citations = retrieval_service.search(query, top_k=3)
    # The retriever should score out-of-domain queries low (< threshold)
    assert len(chunks) == 0
    assert len(citations) == 0
