"""Helpers for reading Claude Code JSONL log files."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List


@dataclass(frozen=True)
class SessionSummary:
    """Minimal information required for indexing a Claude session."""

    leaf_uuid: str
    summary: str
    source_file: Path


class LogParseError(RuntimeError):
    """Raised when a log file cannot be parsed."""


def iter_session_summaries(log_dir: Path) -> Iterator[SessionSummary]:
    """Yield :class:`SessionSummary` objects from ``log_dir``.

    Parameters
    ----------
    log_dir:
        Directory that contains Claude Code JSONL log files.
    """

    if not log_dir.exists():
        raise FileNotFoundError(f"Log directory does not exist: {log_dir}")

    jsonl_files: List[Path] = sorted(p for p in log_dir.rglob("*.jsonl") if p.is_file())
    for path in jsonl_files:
        try:
            yield from _summaries_from_file(path)
        except LogParseError:
            raise
        except Exception as exc:  # pragma: no cover - defensive guard
            raise LogParseError(f"Failed to parse log file {path}") from exc


def _summaries_from_file(path: Path) -> Iterator[SessionSummary]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise LogParseError(
                    f"Invalid JSON on line {line_number} of {path}: {exc}"
                ) from exc

            if payload.get("type") != "summary":
                continue

            leaf_uuid = payload.get("leafUuid")
            summary = payload.get("summary")
            if not leaf_uuid or not summary:
                continue

            yield SessionSummary(leaf_uuid=leaf_uuid, summary=summary, source_file=path)


__all__ = ["SessionSummary", "iter_session_summaries", "LogParseError"]
