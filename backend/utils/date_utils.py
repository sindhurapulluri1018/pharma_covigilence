"""
date_utils.py
=============
Date parsing and proximity calculation utilities.

All date arithmetic for the Duplicate Detection pipeline lives here so
that any date format changes require updates in only one place.
"""

import math
from datetime import date, datetime
from typing import Union


def parse_date(date_str: str) -> date:
    """
    Parse an ISO 8601 date string (YYYY-MM-DD) into a Python date object.

    Parameters
    ----------
    date_str : str
        Date string in YYYY-MM-DD format.

    Returns
    -------
    date
        Parsed date object.

    Raises
    ------
    ValueError
        If the string cannot be parsed.
    """
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(
            f"Cannot parse date '{date_str}'. Expected YYYY-MM-DD format."
        ) from exc


def days_between(date_a: Union[str, date], date_b: Union[str, date]) -> int:
    """
    Return the absolute number of days between two dates.

    Parameters
    ----------
    date_a : str or date
        First date.
    date_b : str or date
        Second date.

    Returns
    -------
    int
        Absolute day difference.
    """
    if isinstance(date_a, str):
        date_a = parse_date(date_a)
    if isinstance(date_b, str):
        date_b = parse_date(date_b)
    return abs((date_a - date_b).days)


def date_proximity_score(
    date_a: Union[str, date],
    date_b: Union[str, date],
    half_life_days: float = 30.0,
) -> float:
    """
    Compute an exponential-decay proximity score between two dates.

    Score = exp(-ln(2) * |days| / half_life_days)

    This means:
      - 0 days apart  → score 1.00
      - half_life days apart → score 0.50
      - 2x half_life apart  → score 0.25
      - etc.

    The half-life is configurable so that late-reporting scenarios common
    in pharmacovigilance (e.g., a case reported 3 months after the event)
    can be tuned without code changes.

    Parameters
    ----------
    date_a : str or date
        First date.
    date_b : str or date
        Second date.
    half_life_days : float
        Number of days at which the score halves (default: 30).

    Returns
    -------
    float
        Proximity score between 0.0 (far apart) and 1.0 (same date).
    """
    delta = days_between(date_a, date_b)
    return math.exp(-math.log(2) * delta / half_life_days)


def is_within_window(
    date_a: Union[str, date],
    date_b: Union[str, date],
    window_days: int,
) -> bool:
    """
    Return True if two dates are within a specified day window.

    Used by the Candidate Retrieval Engine to quickly filter candidates
    before detailed similarity computation.

    Parameters
    ----------
    date_a : str or date
        First date.
    date_b : str or date
        Second date.
    window_days : int
        Maximum allowed day difference.

    Returns
    -------
    bool
        True if |date_a - date_b| <= window_days.
    """
    return days_between(date_a, date_b) <= window_days
