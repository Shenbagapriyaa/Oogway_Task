import math
import re
from typing import List, Dict, Any, Tuple
import logging
from app.services.ingestion_service import ingestion_service
from app.models.schemas import CitationSchema

logger = logging.getLogger(__name__)

class BM25Retriever:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_len: List[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_freqs: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}
        self.corpus_size: int = 0
        self.chunks: List[Dict[str, Any]] = []

    def tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", text.lower())
        stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
            "with", "by", "is", "are", "was", "were", "it", "this", "that", "i", "you",
            "we", "they", "what", "how", "why", "when", "where", "which", "do", "did",
            "have", "has", "had", "so", "just", "like", "know", "think", "about", "there",
            "can", "could", "would", "should", "will"
        }
        return [t for t in tokens if t not in stopwords]

    def fit(self, chunks: List[Dict[str, Any]]):
        self.chunks = chunks
        self.corpus_size = len(chunks)
        if self.corpus_size == 0:
            return

        self.doc_len = []
        self.doc_freqs = []
        df: Dict[str, int] = {}

        for chunk in chunks:
            full_text = f"{chunk['guest']} {chunk['guest']} {chunk['title']} {chunk['title']} {chunk['text']}"
            tokens = self.tokenize(full_text)
            self.doc_len.append(len(tokens))
            frequencies: Dict[str, int] = {}
            for token in tokens:
                frequencies[token] = frequencies.get(token, 0) + 1
            self.doc_freqs.append(frequencies)
            for token in frequencies.keys():
                df[token] = df.get(token, 0) + 1

        self.avg_doc_len = sum(self.doc_len) / self.corpus_size if self.corpus_size > 0 else 0

        for token, freq in df.items():
            self.idf[token] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1.0)

    def search(self, query: str, top_k: int = 4) -> List[Tuple[Dict[str, Any], float]]:
        if self.corpus_size == 0:
            return []

        query_tokens = self.tokenize(query)
        if not query_tokens:
            return []

        scores = [0.0] * self.corpus_size
        matches_found = [0] * self.corpus_size

        for i in range(self.corpus_size):
            cur_doc_len = self.doc_len[i]
            cur_freqs = self.doc_freqs[i]
            score = 0.0

            for token in query_tokens:
                if token in cur_freqs:
                    matches_found[i] += 1
                    freq = cur_freqs[token]
                    idf = self.idf.get(token, 0.0)
                    numerator = freq * (self.k1 + 1.0)
                    denominator = freq + self.k1 * (1.0 - self.b + self.b * (cur_doc_len / (self.avg_doc_len or 1.0)))
                    score += idf * (numerator / denominator)

            # Boost exact guest match
            chunk = self.chunks[i]
            guest_lower = chunk.get("guest", "").lower()
            query_lower = query.lower()
            if guest_lower and any(part in query_lower for part in guest_lower.split() if len(part) > 2):
                score += 8.0
                matches_found[i] += 2

            scores[i] = score

        # Strict relevance threshold: require meaningful token matches and score >= 3.5
        min_matches = max(2, int(len(query_tokens) * 0.35)) if len(query_tokens) >= 3 else 1
        ranked_indices = sorted(range(self.corpus_size), key=lambda idx: scores[idx], reverse=True)
        results = []
        for idx in ranked_indices[:top_k]:
            if scores[idx] >= 3.5 and matches_found[idx] >= min_matches:
                results.append((self.chunks[idx], scores[idx]))

        return results


class RetrievalService:
    def __init__(self):
        self.retriever = BM25Retriever()
        self.is_initialized = False

    def initialize(self):
        chunks = ingestion_service.build_or_load_index()
        self.retriever.fit(chunks)
        self.is_initialized = True
        logger.info(f"RetrievalService initialized with {len(chunks)} indexed chunks.")

    def search(self, query: str, top_k: int = 4) -> Tuple[List[Dict[str, Any]], List[CitationSchema]]:
        if not self.is_initialized:
            self.initialize()

        results = self.retriever.search(query, top_k=top_k * 2)
        query_terms = set(self.retriever.tokenize(query))
        chunks = []
        seen_sources = set()
        guest_was_named = any(
            part in query.lower()
            for chunk in self.retriever.chunks
            for part in chunk.get("guest", "").lower().split()
            if len(part) > 2
        )
        for chunk, _ in results:
            guest_terms = set(self.retriever.tokenize(chunk.get("guest", "")))
            content_terms = query_terms - guest_terms
            guest_turns = [
                turn for turn in ingestion_service.extract_dialogues(chunk.get("text", ""))
                if not turn["speaker"].casefold().startswith("lenny")
            ]
            ranked_turns = [
                (len(content_terms.intersection(self.retriever.tokenize(turn["content"]))), turn)
                for turn in guest_turns
            ]
            best_score, best_turn = max(ranked_turns, key=lambda item: item[0], default=(0, None))
            if guest_was_named and content_terms and best_score == 0:
                continue

            selected = dict(chunk)
            if best_turn and best_score:
                selected["timestamp"] = best_turn["timestamp"]
                text = best_turn["content"]
                matching_terms = content_terms.intersection(self.retriever.tokenize(text))
                term = max(matching_terms, key=len)
                position = text.lower().find(term)
                start = max(0, position - 120)
                end = min(len(text), start + 360)
                quote = text[start:end].strip()
                if start:
                    quote = "..." + quote
                if end < len(text):
                    quote += "..."
                selected["quote"] = quote

            quote_key = re.sub(r"\W+", " ", selected["quote"].casefold()).strip()
            source_key = (selected["guest"].casefold(), selected["title"].casefold(), quote_key)
            if source_key in seen_sources:
                continue
            seen_sources.add(source_key)
            chunks.append(selected)
            if len(chunks) == top_k:
                break
        
        citations = []
        seen_citations = set()
        for c in chunks:
            citation_key = (c["guest"].casefold(), c["title"].casefold(), c["quote"].casefold())
            if citation_key not in seen_citations:
                citations.append(CitationSchema(
                    guest=c["guest"],
                    episode_title=c["title"],
                    timestamp=c["timestamp"],
                    quote=c["quote"]
                ))
                seen_citations.add(citation_key)

        return chunks, citations

retrieval_service = RetrievalService()
