"""
model_manager.py
================
Singleton model manager for the Sentence Transformer embedding model.

Problem solved
--------------
Loading `all-MiniLM-L6-v2` (or any transformer model) takes ~2-5 seconds
and consumes significant RAM.  Letting each service instantiate its own
copy would waste resources and slow every request.

Solution
--------
`ModelManager` follows the Singleton pattern: the model is loaded exactly
once at application startup (via FastAPI's lifespan event) and then
injected into any service that needs it.

Future extensibility
--------------------
Swap the model name in config.py to use:
  - A fine-tuned BioBERT / PubMedBERT model
  - A custom pharmacovigilance embedding model
  - A remote embedding API (OpenAI, Cohere, etc.)

Only this file needs to change.  All downstream services are unaffected.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from core.logger import get_logger

logger = get_logger(__name__)


class ModelManager:
    """
    Singleton wrapper around SentenceTransformer.

    Attributes
    ----------
    _instance : ModelManager or None
        The single shared instance (class-level).
    _model : SentenceTransformer or None
        The loaded embedding model.
    model_name : str
        Name of the loaded model.
    """

    _instance: "ModelManager | None" = None
    _model: SentenceTransformer | None = None
    model_name: str = ""

    # ------------------------------------------------------------------
    # Singleton creation
    # ------------------------------------------------------------------

    def __new__(cls) -> "ModelManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ------------------------------------------------------------------
    # Model loading
    # ------------------------------------------------------------------

    def load(self, model_name: str) -> None:
        """
        Load the Sentence Transformer model.

        Safe to call multiple times – re-uses the already-loaded model
        if the name matches, reloads if a different model name is given.

        Parameters
        ----------
        model_name : str
            HuggingFace model identifier, e.g. 'all-MiniLM-L6-v2'.
        """
        if self._model is not None and self.model_name == model_name:
            logger.info("Model already loaded: %s", model_name)
            return

        logger.info("Loading Sentence Transformer model: %s", model_name)
        self._model = SentenceTransformer(model_name)
        self.model_name = model_name
        logger.info("Model loaded successfully: %s", model_name)

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def encode(self, texts: list[str]) -> np.ndarray:
        """
        Encode a list of text strings into embedding vectors.

        Parameters
        ----------
        texts : list[str]
            List of text strings to encode.

        Returns
        -------
        np.ndarray
            2-D array of shape (len(texts), embedding_dim).

        Raises
        ------
        RuntimeError
            If the model has not been loaded yet.
        """
        if self._model is None:
            raise RuntimeError(
                "ModelManager: model not loaded. "
                "Call model_manager.load(model_name) during app startup."
            )
        return self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    def encode_single(self, text: str) -> np.ndarray:
        """
        Encode a single text string.

        Convenience wrapper around encode().

        Parameters
        ----------
        text : str
            Text to encode.

        Returns
        -------
        np.ndarray
            1-D embedding vector.
        """
        result = self.encode([text])
        return result[0]

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    @property
    def is_loaded(self) -> bool:
        """True if a model has been loaded."""
        return self._model is not None


# ---------------------------------------------------------------------------
# Module-level singleton instance
# ---------------------------------------------------------------------------
# Import this in services that need embeddings:
#   from core.model_manager import model_manager
model_manager = ModelManager()
