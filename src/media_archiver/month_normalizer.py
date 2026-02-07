"""Month folder normalization utilities."""

from __future__ import annotations

import re


_UMLAUT_MAP = str.maketrans({
    "ä": "ae",
    "ö": "oe",
    "ü": "ue",
    "ß": "ss",
})

_MONTHS = {
    "januar": "01_Januar",
    "februar": "02_Februar",
    "maerz": "03_Maerz",
    "april": "04_April",
    "mai": "05_Mai",
    "juni": "06_Juni",
    "juli": "07_Juli",
    "august": "08_August",
    "september": "09_September",
    "oktober": "10_Oktober",
    "november": "11_November",
    "dezember": "12_Dezember",
}


def _normalize_text(value: str) -> str:
    return value.lower().translate(_UMLAUT_MAP)


def _extract_month_tokens(value: str) -> list[str]:
    # Expects tokens separated by spaces after normalization.
    tokens: list[str] = []
    for token in value.split():
        if token.isalpha():
            tokens.append(token)
            continue

        match = re.fullmatch(r"(\d{1,2})([a-z]+)", token)
        if match:
            tokens.append(match.group(2))
            continue

        match = re.fullmatch(r"([a-z]+)(\d{1,4})", token)
        if match:
            tokens.append(match.group(1))
            continue

    return tokens


def normalize_month_folder(name: str) -> str | None:
    if not isinstance(name, str):
        return None

    raw = name.strip()
    if not raw:
        return None

    normalized = _normalize_text(raw.lower())
    normalized = re.sub(r"[\s\-_]+", " ", normalized)

    for token in _extract_month_tokens(normalized):
        canonical = _MONTHS.get(token)
        if canonical is not None:
            return canonical

    return None
