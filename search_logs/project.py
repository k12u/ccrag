"""Utilities for resolving Claude Code project paths."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


CLAUDE_DIR_NAME = ".claude"
PROJECTS_DIR_NAME = "projects"
INDEX_DIR_NAME = "rag-index"


@dataclass(frozen=True)
class ProjectPaths:
    """Collection of important filesystem locations for a project."""

    project_root: Path
    log_dir: Path
    index_dir: Path

    @classmethod
    def from_project_root(cls, project_root: Path) -> "ProjectPaths":
        expanded = project_root.expanduser().resolve()
        identifier = _project_identifier(expanded)
        base_dir = Path.home() / CLAUDE_DIR_NAME
        log_dir = base_dir / PROJECTS_DIR_NAME / identifier
        index_dir = base_dir / INDEX_DIR_NAME / identifier
        return cls(project_root=expanded, log_dir=log_dir, index_dir=index_dir)


def _project_identifier(project_root: Path) -> str:
    """Return the Claude Code identifier for *project_root*.

    Claude Code replaces the ``/`` character in absolute paths with ``-`` and
    prefixes the identifier with a leading ``-``. This helper replicates that
    behaviour so we can locate the matching log directory and cache.
    """

    as_posix = project_root.as_posix()
    if as_posix.startswith("/"):
        as_posix = as_posix[1:]
    identifier = as_posix.replace("/", "-")
    if not identifier.startswith("-"):
        identifier = f"-{identifier}" if identifier else "-"
    return identifier


__all__ = ["ProjectPaths"]
