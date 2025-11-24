from typing import List, Dict, Tuple, Optional

from core.config import (
    SUMMARIZER_MIN_LEN,
    SUMMARIZER_MAX_LEN,
    MAX_TEXT_LENGTH,
)
from core.domain.summarisation_service import BartSummarizer
from core.domain.extraction_service import RuleDateExtractor
from core.infrastructure.asr_service import WhisperLocalTranscriber
from core.infrastructure.export_service import export_meeting_to_pdf

# Instantiate ML services once (can be swapped: maintainability/extensibility)
_transcriber = WhisperLocalTranscriber()
_summarizer = BartSummarizer()
_extractor = RuleDateExtractor()


def summarize_from_text(text: str) -> Tuple[str, List[str], List[Dict[str, str]]]:
    """
    Application layer:
    Text → Summary + Extraction
    """
    text = (text or "").strip()
    if not text:
        return "No content provided.", [], []

    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(
            "Text input too long. Maximum allowed is %d characters." % MAX_TEXT_LENGTH
        )

    summary = _summarizer.summarize(
        text,
        min_len=SUMMARIZER_MIN_LEN,
        max_len=SUMMARIZER_MAX_LEN,
    )
    actions, dates = _extractor.extract(text)
    return summary, actions, dates


def process_audio(
    audio_path: str,
) -> Tuple[str, str, List[str], List[Dict[str, str]]]:
    """
    Application layer:
    Audio → Transcript → Summary + Extraction
    """
    transcript = _transcriber.transcribe(audio_path)
    summary, actions, dates = summarize_from_text(transcript)
    return transcript, summary, actions, dates


def generate_pdf_bytes(
    transcript: Optional[str],
    summary: str,
    actions: List[str],
    dates: List[Dict[str, str]],
) -> bytes:
    """
    Application layer → Export Adapter
    """
    return export_meeting_to_pdf(transcript, summary, actions, dates)
