"""Embedding helpers for Claude Code log search."""

from __future__ import annotations

from typing import List

try:
    import anthropic
except ImportError as exc:  # pragma: no cover - handled at runtime
    anthropic = None  # type: ignore[assignment]

try:
    from chromadb.api.types import Documents
    from chromadb.utils.embedding_functions import EmbeddingFunction
except ImportError as exc:  # pragma: no cover - handled at runtime
    Documents = List[str]  # type: ignore[misc,assignment]

    class EmbeddingFunction:  # type: ignore[no-redef]
        pass


DEFAULT_MODEL = "claude-3-embedding-001"


class AnthropicEmbeddingFunction(EmbeddingFunction):
    """Wrapper that exposes Claude embedding vectors to Chroma."""

    def __init__(self, *, client: "anthropic.Anthropic" | None = None, model: str = DEFAULT_MODEL) -> None:
        if anthropic is None:
            raise RuntimeError(
                "The 'anthropic' package is required for the Claude embedding function."
            )

        self._client = client or anthropic.Anthropic()
        self._model = model

    def __call__(self, texts: Documents) -> List[List[float]]:
        if not texts:
            return []
        response = self._client.embeddings.create(model=self._model, input=texts)
        return [item.embedding for item in response.data]


__all__ = ["AnthropicEmbeddingFunction", "DEFAULT_MODEL"]
