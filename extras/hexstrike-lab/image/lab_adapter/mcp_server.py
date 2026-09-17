#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Any, Callable

from mcp.server.fastmcp import FastMCP

from . import __version__
from .runner import ToolRunner, load_registry


LOGGER = logging.getLogger("hexstrike-lab-adapter")
BASE = Path(os.environ.get("LAB_ADAPTER_ROOT", "/opt/hexstrike-lab"))


def create_server(profile_name: str) -> FastMCP:
    registry = load_registry(BASE / "tools.json")
    profiles = json.loads((BASE / "profiles.json").read_text(encoding="utf-8"))["profiles"]
    if profile_name not in profiles:
        raise ValueError(f"unknown profile: {profile_name}")

    tool_names = _tool_names(profile_name, profiles)
    mcp = FastMCP(f"hexstrike-{profile_name}")

    @mcp.tool(name="tool_inventory")
    def tool_inventory() -> dict[str, Any]:
        """Return the exact tools registered for this profile."""
        return {
            "adapterVersion": __version__,
            "profile": profile_name,
            "tools": [registry[name].__dict__ for name in tool_names if name in registry],
        }

    runner = ToolRunner(profile_name)

    for tool_name in tool_names:
        spec = registry[tool_name]
        handler = _make_handler(runner, spec)
        mcp.tool(name=tool_name)(handler)

    return mcp


def _tool_names(profile_name: str, profiles: dict[str, list[str]]) -> list[str]:
    if profile_name != "lab":
        return profiles[profile_name]
    return sorted(
        {
            tool
            for name, tools in profiles.items()
            if name != "lab"
            for tool in tools
        }
    )


def _make_handler(runner: ToolRunner, spec: Any) -> Callable[..., dict[str, Any]]:
    def invoke(
        asset: str = "",
        target: str = "",
        output_name: str = "",
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run one reviewed lab operation and save its complete output."""
        return runner.run(spec, asset=asset, target=target, output_name=output_name, options=options)

    invoke.__name__ = spec.name
    invoke.__doc__ = f"Run {spec.name} for the {spec.category} lane."
    return invoke


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the optional HexStrike lab adapter")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    create_server(args.profile).run()


if __name__ == "__main__":
    main()
