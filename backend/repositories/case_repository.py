"""
case_repository.py
==================
Repository layer for accessing existing pharmacovigilance cases.

Architecture Pattern
---------------------
This module implements the Repository Pattern:

    DuplicateService
         │
         ▼
    CaseRepository  ← interface (ABC)
         │
    ┌────┴────┐
    ▼         ▼
  JSON      PostgreSQL / MongoDB / FHIR API
 (now)           (future)

Why this matters
----------------
- The Similarity Engine and Candidate Retrieval Engine never touch the
  data layer directly.
- When the team migrates from JSON to a database, ONLY this file changes.
- No other service, router, or test needs modification.

Future implementations
----------------------
Create a new class (e.g., PostgresCaseRepository) that extends
AbstractCaseRepository and override get_all_cases().  Register the
new class in app.py.  Done.
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Optional

from core.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data model (dict-based, intentionally lightweight)
# ---------------------------------------------------------------------------

CaseDict = dict  # Type alias: a single case record as a plain dict


# ---------------------------------------------------------------------------
# Abstract interface
# ---------------------------------------------------------------------------

class AbstractCaseRepository(ABC):
    """
    Abstract base class defining the contract for case data access.

    All concrete repositories must implement these methods.
    The rest of the system depends ONLY on this interface.
    """

    @abstractmethod
    def get_all_cases(self) -> list[CaseDict]:
        """
        Return all existing cases.

        Returns
        -------
        list[CaseDict]
            All cases in the data store.
        """
        ...

    @abstractmethod
    def get_case_by_id(self, case_id: str) -> Optional[CaseDict]:
        """
        Return a single case by its ID, or None if not found.

        Parameters
        ----------
        case_id : str
            The unique case identifier.

        Returns
        -------
        CaseDict or None
        """
        ...

    @abstractmethod
    def count(self) -> int:
        """Return the total number of cases in the store."""
        ...


# ---------------------------------------------------------------------------
# JSON implementation (current)
# ---------------------------------------------------------------------------

class JSONCaseRepository(AbstractCaseRepository):
    """
    Concrete repository that reads cases from a JSON file.

    The file is read ONCE at instantiation and cached in memory.
    This matches the requirement that the data layer does not reload
    on every request.

    Swap this for PostgresCaseRepository / MongoCaseRepository when
    the team is ready to move off JSON files.

    Parameters
    ----------
    file_path : str
        Path to the JSON file containing existing cases.
    """

    def __init__(self, file_path: str) -> None:
        self._file_path = file_path
        self._cases: list[CaseDict] = []
        self._case_index: dict[str, CaseDict] = {}
        self._load()

    def _load(self) -> None:
        """Load and index cases from the JSON file."""
        if not os.path.exists(self._file_path):
            logger.error("Case file not found: %s", self._file_path)
            self._cases = []
            return

        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                self._cases = json.load(f)

            # Build an O(1) lookup index by case_id
            self._case_index = {c["case_id"]: c for c in self._cases}

            logger.info(
                "JSONCaseRepository loaded %d cases from %s",
                len(self._cases),
                self._file_path,
            )
        except (json.JSONDecodeError, IOError) as exc:
            logger.error("Failed to load case file: %s | error: %s", self._file_path, exc)
            self._cases = []
            self._case_index = {}

    def get_all_cases(self) -> list[CaseDict]:
        """Return all cached cases."""
        return self._cases

    def get_case_by_id(self, case_id: str) -> Optional[CaseDict]:
        """O(1) lookup by case_id."""
        return self._case_index.get(case_id)

    def count(self) -> int:
        """Return total number of loaded cases."""
        return len(self._cases)


# ---------------------------------------------------------------------------
# Stub implementations for future databases (uncomment when ready)
# ---------------------------------------------------------------------------

# class PostgresCaseRepository(AbstractCaseRepository):
#     """Future: reads from PostgreSQL using asyncpg or SQLAlchemy."""
#     def __init__(self, connection_string: str): ...
#     def get_all_cases(self) -> list[CaseDict]: ...
#     def get_case_by_id(self, case_id: str) -> Optional[CaseDict]: ...
#     def count(self) -> int: ...

# class MongoCaseRepository(AbstractCaseRepository):
#     """Future: reads from MongoDB using motor or pymongo."""
#     def __init__(self, uri: str, db: str, collection: str): ...
#     def get_all_cases(self) -> list[CaseDict]: ...
#     def get_case_by_id(self, case_id: str) -> Optional[CaseDict]: ...
#     def count(self) -> int: ...
