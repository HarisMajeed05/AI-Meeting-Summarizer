import re
from abc import ABC
from typing import List, Dict, Tuple, Optional
from datetime import date, timedelta

from core.domain.summarisation_service import Chunker


# ------------------------------------------------------------
# ACTION WORD DETECTION
# ------------------------------------------------------------
ACTION_PAT = re.compile(
    r"\b(should|to do|action|follow up|deadline|assign|send|prepare|review|meet|schedule|email|submit|call)\b",
    re.IGNORECASE,
)


# ------------------------------------------------------------
# WEEKDAY HANDLING
# ------------------------------------------------------------
WEEKDAY_TO_INDEX = {
    "monday": 0, "tuesday": 1, "wednesday": 2,
    "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
}

WEEKDAY_REGEX = re.compile(
    r"\b(next|this)?\s*(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    re.IGNORECASE
)


# ------------------------------------------------------------
# MONTH HANDLING
# ------------------------------------------------------------
MONTH_NAME_TO_NUM = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}

DAY_MONTH_REGEX = re.compile(
    r"\b(\d{1,2})(?:st|nd|rd|th)?\s+"
    r"(january|february|march|april|may|june|july|august|september|october|november|december|"
    r"jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)"
    r"\s*(\d{4})?\b",
    re.IGNORECASE,
)

MONTH_DAY_REGEX = re.compile(
    r"\b("
    r"january|february|march|april|may|june|july|august|september|october|november|december|"
    r"jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec"
    r")\s+(\d{1,2})(?:st|nd|rd|th)?\s*(\d{4})?\b",
    re.IGNORECASE,
)


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def _make_date(day: int, month: int, year: Optional[int]) -> date:
    """
    Explicit year → ALWAYS respected exactly.
    Missing year → use current year, push future if needed.
    """
    today = date.today()

    if year is None:
        year = today.year
        d = date(year, month, day)
        if d < today:
            d = date(year + 1, month, day)
        return d

    # Explicit year
    return date(year, month, day)


# ------------------------------------------------------------
# DATE PARSERS
# ------------------------------------------------------------
def compute_weekday_dates(sentence: str) -> List[Dict[str, str]]:
    today = date.today()
    results = []

    for m in WEEKDAY_REGEX.finditer(sentence):
        prefix = m.group(1).lower() if m.group(1) else None
        weekday = m.group(2).lower()

        target_idx = WEEKDAY_TO_INDEX[weekday]
        today_idx = today.weekday()

        diff = target_idx - today_idx
        if prefix == "next":
            if diff <= 0:
                diff += 7
            diff += 7
        elif prefix == "this":
            if diff < 0:
                diff += 7
        else:
            if diff < 0:
                diff += 7

        d = today + timedelta(days=diff)
        results.append({
            "date": d.strftime("%Y-%m-%d"),
            "context": sentence
        })

    return results


def compute_day_month_dates(sentence: str) -> List[Dict[str, str]]:
    results = []

    # Day Month Year
    for day_str, month_str, year_str in DAY_MONTH_REGEX.findall(sentence):
        day = int(day_str)
        month = MONTH_NAME_TO_NUM[month_str.lower()]
        year = int(year_str) if year_str else None
        d = _make_date(day, month, year)
        results.append({"date": d.strftime("%Y-%m-%d"), "context": sentence})

    # Month Day Year
    for month_str, day_str, year_str in MONTH_DAY_REGEX.findall(sentence):
        day = int(day_str)
        month = MONTH_NAME_TO_NUM[month_str.lower()]
        year = int(year_str) if year_str else None
        d = _make_date(day, month, year)
        results.append({"date": d.strftime("%Y-%m-%d"), "context": sentence})

    return results


# ------------------------------------------------------------
# MAIN EXTRACTOR
# ------------------------------------------------------------
class IExtractor(ABC):
    def extract(self, text: str) -> Tuple[List[str], List[Dict[str, str]]]:
        raise NotImplementedError


class RuleDateExtractor(IExtractor):

    def extract(self, text: str) -> Tuple[List[str], List[Dict[str, str]]]:
        actions = []
        dates = []

        for sent in Chunker.split_sentences(text):
            # Action detection
            if ACTION_PAT.search(sent):
                actions.append(sent)

            # Date extraction
            dates.extend(compute_weekday_dates(sent))
            dates.extend(compute_day_month_dates(sent))
            # NO NUMERIC DATES ON PURPOSE

        # ----------------------------------------------------
        # MERGE BY CONTEXT (NO DUPLICATES)
        # ----------------------------------------------------
        merged = {}

        for d in dates:
            ctx = d["context"].strip()
            dt = d["date"]

            if ctx not in merged:
                merged[ctx] = []

            if dt not in merged[ctx]:
                merged[ctx].append(dt)

        final_dates = []
        for ctx, dt_list in merged.items():
            final_dates.append({
                "date": ", ".join(dt_list),
                "context": ctx
            })

        return actions, final_dates
