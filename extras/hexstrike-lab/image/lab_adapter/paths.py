from __future__ import annotations

import os
from pathlib import Path


class PathBoundaryError(ValueError):
    """Raised when a requested path escapes a workbench boundary."""


INPUT_ROOT = Path(os.environ.get("LAB_INPUT_ROOT", "/workbench/input"))
OUTPUT_ROOT = Path(os.environ.get("LAB_OUTPUT_ROOT", "/workbench/output"))


def _resolve_under(root: Path, relative: str, *, must_exist: bool) -> Path:
    if not relative or Path(relative).is_absolute():
        raise PathBoundaryError("path must be a non-empty relative path")
    if ".." in Path(relative).parts:
        raise PathBoundaryError("parent traversal is not allowed")

    resolved_root = root.resolve(strict=True)
    candidate = (resolved_root / relative).resolve(strict=must_exist)
    try:
        candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise PathBoundaryError("path escapes the workbench boundary") from exc
    return candidate


def input_path(relative: str) -> Path:
    candidate = _resolve_under(INPUT_ROOT, relative, must_exist=True)
    if candidate.is_dir():
        _validate_tree_symlinks(candidate, INPUT_ROOT.resolve(strict=True))
    return candidate


def output_path(relative: str, *, must_exist: bool = False) -> Path:
    return _resolve_under(OUTPUT_ROOT, relative, must_exist=must_exist)


def display_path(path: Path) -> str:
    for label, root in (("input", INPUT_ROOT), ("output", OUTPUT_ROOT)):
        try:
            return f"{label}/{path.resolve().relative_to(root.resolve())}"
        except ValueError:
            continue
    return path.name


def _validate_tree_symlinks(directory: Path, root: Path) -> None:
    for child in directory.rglob("*"):
        if not child.is_symlink():
            continue
        try:
            child.resolve(strict=True).relative_to(root)
        except (FileNotFoundError, ValueError) as exc:
            raise PathBoundaryError(f"symlink escapes the input boundary: {child.name}") from exc
