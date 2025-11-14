"""Command line interface for Claude Code log search."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from .embedding import AnthropicEmbeddingFunction
from .indexer import IndexManager
from .logs import LogParseError, iter_session_summaries
from .project import ProjectPaths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Search Claude Code session logs using retrieval-augmented generation techniques.",
    )
    parser.add_argument("query", help="Natural language query to search for.")
    parser.add_argument(
        "--project-path",
        type=Path,
        default=Path.cwd(),
        help="Project root directory. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results to return (default: 5).",
    )
    parser.add_argument(
        "--show-summary",
        action="store_true",
        help="Display the stored summary text alongside each result.",
    )
    parser.add_argument(
        "--show-distance",
        action="store_true",
        help="Display the vector distance returned by Chroma for each result.",
    )
    parser.add_argument(
        "--force-reindex",
        action="store_true",
        help="Rebuild the Chroma index even if it appears up to date.",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    project_paths = ProjectPaths.from_project_root(args.project_path)
    log_dir = project_paths.log_dir

    try:
        summaries = list(iter_session_summaries(log_dir))
    except FileNotFoundError:
        print(f"Log directory does not exist: {log_dir}", file=sys.stderr)
        return 2
    except LogParseError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not summaries:
        print("No session summaries were found in the Claude log directory.", file=sys.stderr)
        return 1

    try:
        embedding_function = AnthropicEmbeddingFunction()
        indexer = IndexManager(index_dir=project_paths.index_dir, embedding_function=embedding_function)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    indexer.ensure_index(log_dir=log_dir, summaries=summaries, force=args.force_reindex)

    results = indexer.search(args.query, top_k=args.top_k)
    if not results:
        print("No matching sessions were found.")
        return 0

    for result in results:
        parts = [result.leaf_uuid]
        if args.show_distance and result.distance is not None:
            parts.append(f"distance={result.distance:.4f}")
        if args.show_summary and result.summary:
            parts.append(result.summary)
        print(" \u2014 ".join(parts))

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
