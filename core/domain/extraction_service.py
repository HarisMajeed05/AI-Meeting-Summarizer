import re
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple

from dateparser.search import search_dates

from core.domain.summarisation_service import Chunker
from core.config import DATE_ORDER

ACTION_PAT = re.compile(
    r"\b(should|to do|action|follow up|deadline|assign|send|prepare|review|meet|schedule|email|submit|call)\b",
    re.IGNORECASE,
)


class IExtractor(ABC):
    def extract(self, text: str) -> Tuple[List[str], List[Dict[str, str]]]:
        raise NotImplementedError


class RuleDateExtractor(IExtractor):
    """
    Rule-based extraction:
    - Action items (sentences matching ACTION_PAT)
    - Dates via dateparser.search_dates
    """

    def extract(self, text: str) -> Tuple[List[str], List[Dict[str, str]]]:
        actions = []
        dates = []

        for sent in Chunker.split_sentences(text):
            if ACTION_PAT.search(sent):
                actions.append(sent)

            found = search_dates(
                sent,
                settings={
                    "DATE_ORDER": DATE_ORDER,
                    "RETURN_AS_TIMEZONE_AWARE": False,
                },
            )
            if found:
                for _, dt in found:
                    dates.append(
                        {
                            "date": dt.strftime("%Y-%m-%d"),
                            "context": sent,
                        }
                    )

        # Optionally deduplicate
        unique = []
        seen = set()
        for d in dates:
            key = (d["date"], d["context"])
            if key not in seen:
                seen.add(key)
                unique.append(d)

        return actions, unique
