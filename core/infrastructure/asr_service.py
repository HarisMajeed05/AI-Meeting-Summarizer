import os
from abc import ABC, abstractmethod
from typing import Optional

import torch
from transformers import pipeline
from huggingface_hub import InferenceClient

from core.config import ASR_MODEL_NAME, HF_API_KEY


class ITranscriber(ABC):
    """
    Interface for ASR services.
    """

    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        raise NotImplementedError


class WhisperLocalTranscriber(ITranscriber):
    """
    Local ASR using Whisper via transformers.pipeline.

    This matches the doc:
    - Purpose: convert audio → text.
    """

    def __init__(self, model_name: str = ASR_MODEL_NAME, device: Optional[int] = None):
        if device is None:
            device = 0 if torch.cuda.is_available() else -1

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=model_name,
            generate_kwargs={"language": "en", "task": "transcribe"},
            device=device,
        )

    def transcribe(self, audio_path: str) -> str:
        if not os.path.exists(audio_path):
            raise FileNotFoundError("Audio file not found: %s" % audio_path)

        result = self.pipe(audio_path)
        if isinstance(result, dict):
            return result.get("text", "")
        return str(result)


class HFAPITranscriber(ITranscriber):
    """
    Optional ASR via Hugging Face Inference API.

    Internal structure matches your doc's example:

    class HFAPITranscriber(ITranscriber):
        def __init__(self, api_key: str, model_name="openai/whisper-base"):
            self.client = InferenceClient(api_key=api_key)
            self.model_name = model_name
        def transcribe(self, audio_path: str) -> str:
            result = self.client.audio_to_text(audio_path, model=self.model_name)
            return result["text"]
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = ASR_MODEL_NAME,
    ):
        if api_key is None:
            api_key = HF_API_KEY
        if not api_key:
            raise ValueError("HF_API_KEY not configured; cannot use HFAPITranscriber")

        self.client = InferenceClient(api_key=api_key)
        self.model_name = model_name

    def transcribe(self, audio_path: str) -> str:
        # NOTE: This follows your doc's example; adapted for illustration.
        # Actual method signature on InferenceClient may differ.
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        # Hypothetical usage; in practice you'd align with HF's actual audio API.
        result = self.client.audio_to_text(audio_bytes, model=self.model_name)
        return result["text"]
