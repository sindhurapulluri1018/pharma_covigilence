"""
text_utils.py
=============
Text normalisation and cleaning utilities for the Similarity Engine.

Design note – future extensibility stubs
-----------------------------------------
Two stubs are provided that will be filled in when external dictionaries
are integrated:

  normalize_drug_name()  → WHO Drug Dictionary (INN lookup)
  expand_reaction_synonyms() → MedDRA preferred-term expansion

Keeping them here means the Similarity Engine never needs to change;
only this utility module is updated.
"""

import re
import string
from typing import Optional


# ---------------------------------------------------------------------------
# Common English stop words relevant to pharmacovigilance narratives
# ---------------------------------------------------------------------------
_STOP_WORDS: frozenset[str] = frozenset(
    {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "is", "was", "are", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "will", "would", "could", "should", "may", "might", "shall",
        "patient", "patients", "reported", "report", "after", "before",
        "developed", "taking", "experienced", "following",
    }
)


def clean_text(text: str) -> str:
    """
    Lowercase, strip punctuation, collapse whitespace.

    Used as a pre-processing step before fuzzy or embedding-based comparison.

    Parameters
    ----------
    text : str
        Raw text string.

    Returns
    -------
    str
        Cleaned text.
    """
    if not text:
        return ""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def remove_stop_words(text: str) -> str:
    """
    Remove common stop words from a cleaned text string.

    Parameters
    ----------
    text : str
        Already cleaned (lowercased, no punctuation) text.

    Returns
    -------
    str
        Text with stop words removed.
    """
    tokens = text.split()
    return " ".join(t for t in tokens if t not in _STOP_WORDS)


def extract_keywords(text: str, max_keywords: int = 10) -> list[str]:
    """
    Extract meaningful keywords from a text string.

    Used by the Candidate Retrieval Engine for reaction-keyword fallback.

    Parameters
    ----------
    text : str
        Raw text to extract keywords from.
    max_keywords : int
        Maximum number of keywords to return.

    Returns
    -------
    list[str]
        List of keyword strings.
    """
    cleaned = remove_stop_words(clean_text(text))
    tokens = cleaned.split()
    # Return unique tokens, preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for t in tokens:
        if t not in seen and len(t) > 2:
            seen.add(t)
            unique.append(t)
    return unique[:max_keywords]


def keyword_overlap_score(text_a: str, text_b: str) -> float:
    """
    Compute a simple keyword overlap ratio between two texts.

    Used as a lightweight fallback in Candidate Retrieval.

    Parameters
    ----------
    text_a : str
        First text.
    text_b : str
        Second text.

    Returns
    -------
    float
        Overlap score between 0.0 and 1.0.
    """
    kw_a = set(extract_keywords(text_a))
    kw_b = set(extract_keywords(text_b))
    if not kw_a or not kw_b:
        return 0.0
    intersection = kw_a & kw_b
    union = kw_a | kw_b
    return len(intersection) / len(union)


# ---------------------------------------------------------------------------
# Extensibility stubs
# ---------------------------------------------------------------------------


def normalize_drug_name(drug_name: str) -> str:
    """
    Normalize a drug name to its WHO INN (International Nonproprietary Name).

    STUB – currently returns the cleaned input unchanged.

    Future implementation
    ---------------------
    1. Query WHO Drug Dictionary API / local SQLite copy.
    2. Return the INN for the given brand name or synonym.
    3. If not found, return the cleaned input as-is.

    Parameters
    ----------
    drug_name : str
        Drug name as reported (brand or INN).

    Returns
    -------
    str
        Normalised INN name (or original if not found in dictionary).
    """
    # TODO: integrate WHO Drug Dictionary
    return clean_text(drug_name)


def expand_reaction_synonyms(reaction_term: str) -> list[str]:
    """
    Expand an adverse reaction term to its MedDRA preferred-term synonyms.

    STUB – currently returns a single-element list with the original term.

    Future implementation
    ---------------------
    1. Query MedDRA hierarchy for the Lowest Level Term (LLT).
    2. Return the Preferred Term (PT) and related synonyms.
    3. Use the expanded list for richer similarity comparison.

    Parameters
    ----------
    reaction_term : str
        Adverse reaction as reported.

    Returns
    -------
    list[str]
        List of synonym terms (at minimum the original term).
    """
    # TODO: integrate MedDRA
    return [clean_text(reaction_term)]
