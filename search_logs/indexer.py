"""Chroma index management for Claude Code logs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Set

try:
    import chromadb
except ImportError:  # pragma: no cover - handled at runtime
    chromadb = None  # type: ignore[assignment]

from .embedding import AnthropicEmbeddingFunction
from .logs import SessionSummary


@dataclass
class SearchResult:
    leaf_uuid: str
    summary: str
    distance: float | None


class IndexManager:
    """Build and query a Chroma index for Claude Code session summaries."""

    def __init__(
        self,
        *,
        index_dir: Path,
        embedding_function: AnthropicEmbeddingFunction,
        collection_name: str = "claude-code-session-summaries",
    ) -> None:
        if chromadb is None:
            raise RuntimeError("The 'chromadb' package is required for indexing logs.")

        self._index_dir = index_dir
        self._index_dir.mkdir(parents=True, exist_ok=True)
        self._embedding_function = embedding_function
        self._collection_name = collection_name
        self._metadata_path = index_dir / "metadata.json"
        self._client = chromadb.PersistentClient(path=str(index_dir))

    def ensure_index(
        self,
        *,
        log_dir: Path,
        summaries: Iterable[SessionSummary],
        force: bool = False,
    ) -> None:
        self._index_dir.mkdir(parents=True, exist_ok=True)
        latest_mtime = _latest_mtime(log_dir)
        metadata = _read_metadata(self._metadata_path)
        needs_rebuild = force or _should_rebuild(metadata, log_dir, latest_mtime)

        if not needs_rebuild:
            return

        collection = self._get_collection()
        collection.delete(where={})

        docs: List[str] = []
        ids: List[str] = []
        metadatas: List[dict[str, str]] = []
        seen_ids: Set[str] = set()
        for summary in summaries:
            if summary.leaf_uuid in seen_ids:
                continue
            seen_ids.add(summary.leaf_uuid)
            docs.append(summary.summary)
            ids.append(summary.leaf_uuid)
            metadatas.append(
                {
                    "leaf_uuid": summary.leaf_uuid,
                    "source_file": str(summary.source_file),
                }
            )

        if docs:
            collection.add(documents=docs, ids=ids, metadatas=metadatas)

        _write_metadata(
            self._metadata_path,
            {
                "log_dir": str(log_dir),
                "latest_log_mtime": latest_mtime,
                "collection_name": self._collection_name,
            },
        )

    def search(self, query: str, *, top_k: int = 5) -> List[SearchResult]:
        collection = self._get_collection()
        result = collection.query(query_texts=[query], n_results=top_k, include=["distances", "metadatas", "documents"])

        results: List[SearchResult] = []
        metadatas = result.get("metadatas") or []
        documents = result.get("documents") or []
        distances = result.get("distances") or []

        for metadata_list, document_list, distance_list in zip(metadatas, documents, distances):
            for metadata, document, distance in zip(metadata_list, document_list, distance_list):
                leaf_uuid = metadata.get("leaf_uuid") if metadata else None
                if not leaf_uuid:
                    continue
                results.append(
                    SearchResult(
                        leaf_uuid=leaf_uuid,
                        summary=document,
                        distance=distance,
                    )
                )
        return results

    def _get_collection(self):
        return self._client.get_or_create_collection(
            name=self._collection_name, embedding_function=self._embedding_function
        )


def _latest_mtime(directory: Path) -> float:
    if not directory.exists():
        return 0.0
    mtimes = [path.stat().st_mtime for path in directory.rglob("*") if path.is_file()]
    return max(mtimes, default=0.0)


def _read_metadata(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:  # pragma: no cover - defensive
        return {}


def _write_metadata(path: Path, metadata: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle)


def _should_rebuild(metadata: dict[str, object], log_dir: Path, latest_mtime: float) -> bool:
    if not metadata:
        return True
    if metadata.get("log_dir") != str(log_dir):
        return True
    try:
        stored_mtime = float(metadata.get("latest_log_mtime", 0.0))
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return True
    return latest_mtime > stored_mtime


__all__ = ["IndexManager", "SearchResult"]
