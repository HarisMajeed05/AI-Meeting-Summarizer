import re
from abc import ABC, abstractmethod
from typing import List

from transformers import pipeline

from core.config import (
    SUMMARIZER_MAX_LEN,
    SUMMARIZER_MIN_LEN,
    CHUNK_MAX_CHARS,
    SUMMARIZER_MODEL_NAME,
    TOKENIZER_MODEL_MAX_LENGTH,
)


class ISummarizer(ABC):
    def summarize(self, text: str, min_len: int, max_len: int) -> str:
        raise NotImplementedError


class Chunker:
    @staticmethod
    def split_sentences(text: str) -> List[str]:
        return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

    @staticmethod
    def chunk(text: str, max_chars: int = CHUNK_MAX_CHARS) -> List[str]:
        parts = []
        buf = ""
        for sent in Chunker.split_sentences(text):
            if len(buf) + len(sent) + 1 <= max_chars:
                buf += (" " if buf else "") + sent
            else:
                parts.append(buf)
                buf = sent
        if buf:
            parts.append(buf)
        return parts


class BartSummarizer(ISummarizer):
    def __init__(self, model: str = SUMMARIZER_MODEL_NAME):
        self.pipe = pipeline("summarization", model=model)
        # Make tokenizer aware of sensible ceiling to avoid warnings
        self.pipe.tokenizer.model_max_length = TOKENIZER_MODEL_MAX_LENGTH

    def summarize(self, text: str, min_len: int = SUMMARIZER_MIN_LEN, max_len: int = SUMMARIZER_MAX_LEN) -> str:
        parts = Chunker.chunk(text)
        if not parts:
            return "No content provided."

        partials = [
            self.pipe(
                p,
                max_length=max_len,
                min_length=min_len,
                do_sample=False,
                truncation=True,
            )[0]["summary_text"]
            for p in parts
        ]

        combined = " ".join(partials)
        if len(parts) > 1:
            final = self.pipe(
                combined,
                max_length=max_len,
                min_length=min_len,
                do_sample=False,
                truncation=True,
            )[0]["summary_text"]
            return final
        return combined
