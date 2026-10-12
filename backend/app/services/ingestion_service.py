import os
import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class IngestionService:
    def __init__(self, transcripts_dir: Path = settings.TRANSCRIPTS_DIR, cache_dir: Path = settings.CACHE_DIR):
        self.transcripts_dir = transcripts_dir
        self.cache_file = cache_dir / "index_cache.json"
        self.chunks: List[Dict[str, Any]] = []

    def parse_frontmatter(self, text: str) -> tuple[Dict[str, Any], str]:
        """Extract YAML-style frontmatter from markdown file."""
        frontmatter = {}
        body = text
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                raw_fm = parts[1].strip()
                body = parts[2].strip()
                for line in raw_fm.split("\n"):
                    if ":" in line:
                        key, val = line.split(":", 1)
                        clean_val = val.strip().strip('"').strip("'")
                        frontmatter[key.strip()] = clean_val
        return frontmatter, body

    def extract_dialogues(self, body: str) -> List[Dict[str, str]]:
        """Extract speaker turns with timestamps."""
        pattern = r"\*\*([^*]+)\*\*\s*\(([^)]+)\):\s*([\s\S]*?)(?=(?:\*\*[^*]+\*\*\s*\([^)]+\):|$))"
        matches = re.findall(pattern, body)
        dialogues = []
        for speaker, timestamp, content in matches:
            clean_content = content.strip()
            if clean_content:
                dialogues.append({
                    "speaker": speaker.strip(),
                    "timestamp": timestamp.strip(),
                    "content": clean_content
                })
        return dialogues

    @staticmethod
    def infer_guest(dialogues: List[Dict[str, str]], fallback: str) -> str:
        speakers = list(dict.fromkeys(
            turn["speaker"] for turn in dialogues
            if not turn["speaker"].casefold().startswith("lenny")
        ))
        return ", ".join(speakers) if speakers else fallback

    def chunk_dialogues(self, dialogues: List[Dict[str, str]], metadata: Dict[str, Any], max_words: int = 400) -> List[Dict[str, Any]]:
        """Combine speaker turns into coherent chunks with overlap."""
        chunks = []
        current_chunk_turns = []
        current_words = 0

        for turn in dialogues:
            turn_words = len(turn["content"].split())
            if current_words + turn_words > max_words and current_chunk_turns:
                # Flush current chunk
                first_turn = current_chunk_turns[0]
                chunk_text = "\n\n".join([f"**{t['speaker']}** ({t['timestamp']}): {t['content']}" for t in current_chunk_turns])
                
                # Representative quote
                quote_turn = next((t for t in current_chunk_turns if t['speaker'] != "Lenny Rachitsky"), first_turn)
                quote_snippet = quote_turn['content'][:250].strip() + ("..." if len(quote_turn['content']) > 250 else "")

                chunks.append({
                    "id": f"{metadata.get('slug', 'ep')}_{len(chunks)}",
                    "title": metadata.get("title", "Lenny's Podcast"),
                    "guest": metadata.get("guest", metadata.get("title", "Guest")),
                    "date": metadata.get("date", "Unknown"),
                    "timestamp": first_turn["timestamp"],
                    "text": chunk_text,
                    "quote": quote_snippet,
                    "word_count": current_words
                })
                # Overlap: keep the last turn
                current_chunk_turns = [current_chunk_turns[-1]]
                current_words = len(current_chunk_turns[0]["content"].split())

            current_chunk_turns.append(turn)
            current_words += turn_words

        if current_chunk_turns:
            first_turn = current_chunk_turns[0]
            chunk_text = "\n\n".join([f"**{t['speaker']}** ({t['timestamp']}): {t['content']}" for t in current_chunk_turns])
            quote_turn = next((t for t in current_chunk_turns if t['speaker'] != "Lenny Rachitsky"), first_turn)
            quote_snippet = quote_turn['content'][:250].strip() + ("..." if len(quote_turn['content']) > 250 else "")

            chunks.append({
                "id": f"{metadata.get('slug', 'ep')}_{len(chunks)}",
                "title": metadata.get("title", "Lenny's Podcast"),
                "guest": metadata.get("guest", metadata.get("title", "Guest")),
                "date": metadata.get("date", "Unknown"),
                "timestamp": first_turn["timestamp"],
                "text": chunk_text,
                "quote": quote_snippet,
                "word_count": current_words
            })

        return chunks

    def build_or_load_index(self, force_reload: bool = False) -> List[Dict[str, Any]]:
        """Build chunks from transcripts or load from cached json."""
        if not force_reload and self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
                for chunk in self.chunks:
                    dialogues = self.extract_dialogues(chunk.get("text", ""))
                    chunk["guest"] = self.infer_guest(dialogues, chunk.get("guest", "Guest"))
                logger.info(f"Loaded {len(self.chunks)} chunks from cache ({self.cache_file}).")
                return self.chunks
            except Exception as e:
                logger.warning(f"Failed to read cache ({e}), rebuilding index.")

        if not self.transcripts_dir.exists():
            logger.warning(f"Transcripts directory not found at {self.transcripts_dir}")
            return []

        all_chunks = []
        files = list(self.transcripts_dir.glob("*.md"))
        logger.info(f"Found {len(files)} markdown transcripts in {self.transcripts_dir}.")

        for filepath in files:
            try:
                content = filepath.read_text(encoding="utf-8", errors="replace")
                fm, body = self.parse_frontmatter(content)
                fm["slug"] = filepath.stem
                if not fm.get("title"):
                    fm["title"] = filepath.stem.replace("-", " ").title()
                if not fm.get("guest"):
                    fm["guest"] = fm["title"]

                dialogues = self.extract_dialogues(body)
                if dialogues:
                    fm["guest"] = self.infer_guest(dialogues, fm["guest"])
                    file_chunks = self.chunk_dialogues(dialogues, fm)
                else:
                    # Fallback plain paragraph chunking if speaker tags are absent
                    words = body.split()
                    file_chunks = []
                    step = 350
                    for i in range(0, len(words), step):
                        chunk_words = words[i:i + step]
                        file_chunks.append({
                            "id": f"{fm['slug']}_{len(file_chunks)}",
                            "title": fm["title"],
                            "guest": fm["guest"],
                            "date": fm.get("date", "Unknown"),
                            "timestamp": "00:00:00",
                            "text": " ".join(chunk_words),
                            "quote": " ".join(chunk_words[:40]) + "...",
                            "word_count": len(chunk_words)
                        })
                all_chunks.extend(file_chunks)
            except Exception as e:
                logger.error(f"Error processing transcript {filepath.name}: {e}")

        self.chunks = all_chunks
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(all_chunks, f, ensure_ascii=False)
            logger.info(f"Indexed and cached {len(all_chunks)} chunks to {self.cache_file}.")
        except Exception as e:
            logger.warning(f"Could not save cache to {self.cache_file}: {e}")

        return self.chunks

ingestion_service = IngestionService()
