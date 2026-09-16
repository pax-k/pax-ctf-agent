#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config/coverage.json"
OUTPUT = ROOT / "docs/coverage-matrix.md"


def render() -> str:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    lines = [
        "# OmniCTF Coverage Matrix",
        "",
        "This file is generated from `config/coverage.json`. Do not edit it directly.",
        "",
        "| Category | Subdomain | Owner | Profile | Skill | Tool | Validation |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for capability in data["capabilities"]:
        lines.append(
            "| {category} | {subdomain} | {owner} | {profile} | {skill} | {installedTool} | {validationLevel} |".format(
                **{key: (value if value is not None else "-") for key, value in capability.items()}
            )
        )
    lines.extend(
        [
            "",
            "A listed capability is a repository commitment only at its stated validation level. "
            "Live event acceptance remains separate from fixture and smoke evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render()
    if args.check:
        actual = OUTPUT.read_text(encoding="utf-8")
        if actual != expected:
            raise SystemExit("docs/coverage-matrix.md is not synchronized")
    else:
        OUTPUT.write_text(expected, encoding="utf-8")


if __name__ == "__main__":
    main()
