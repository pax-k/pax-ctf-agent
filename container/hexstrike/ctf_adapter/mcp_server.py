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
from .koth import apply_patch, prepare_flag_submission, prepare_patch, snapshot, submit_flag
from .runner import ToolRunner, load_registry
from .scope import EngagementScope


LOGGER = logging.getLogger("omnictf-ctf-adapter")
BASE = Path(os.environ.get("CTF_ADAPTER_ROOT", "/opt/ctf-adapter"))


def create_server(profile_name: str) -> FastMCP:
    registry = load_registry(BASE / "tools.json")
    profiles = json.loads((BASE / "profiles.json").read_text(encoding="utf-8"))["profiles"]
    if profile_name not in profiles:
        raise ValueError(f"unknown profile: {profile_name}")

    mcp = FastMCP(f"hexstrike-{profile_name}")

    @mcp.tool(name="tool_inventory")
    def tool_inventory() -> dict[str, Any]:
        """Return the exact tools registered for this profile."""
        names = profiles[profile_name]
        return {
            "adapterVersion": __version__,
            "profile": profile_name,
            "tools": [registry[name].__dict__ for name in names if name in registry],
        }

    if profile_name == "catalog":
        return mcp

    scope = EngagementScope.load()
    runner = ToolRunner(scope, profile_name)

    for tool_name in profiles[profile_name]:
        if tool_name.startswith("koth_"):
            continue
        spec = registry[tool_name]
        handler = _make_handler(runner, spec)
        mcp.tool(name=tool_name)(handler)

    if profile_name == "koth":
        _register_koth_tools(mcp, scope)
    return mcp


def _make_handler(runner: ToolRunner, spec: Any) -> Callable[..., dict[str, Any]]:
    def invoke(
        asset: str = "",
        target: str = "",
        output_name: str = "",
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run one reviewed CTF operation and save its complete evidence."""
        return runner.run(spec, asset=asset, target=target, output_name=output_name, options=options)

    invoke.__name__ = spec.name
    invoke.__doc__ = f"Run {spec.name} for the {spec.category} lane."
    return invoke


def _register_koth_tools(mcp: FastMCP, scope: EngagementScope) -> None:
    @mcp.tool(name="koth_snapshot")
    def koth_snapshot(source: str, name: str) -> dict[str, Any]:
        """Copy an input service tree to the writable KOTH workspace."""
        return snapshot(source, name)

    @mcp.tool(name="koth_prepare_patch")
    def koth_prepare_patch(patch_asset: str, checkout: str) -> dict[str, Any]:
        """Validate a patch and return the exact digest that needs human approval."""
        return prepare_patch(scope, patch_asset, checkout)

    @mcp.tool(name="koth_apply_patch")
    def koth_apply_patch(bundle: str, approval_digest: str) -> dict[str, Any]:
        """Apply only the exact patch bundle approved by its digest."""
        return apply_patch(scope, bundle, approval_digest)

    @mcp.tool(name="koth_prepare_flag_submission")
    def koth_prepare_flag_submission(
        flag: str, target: str, team: str, endpoint: str
    ) -> dict[str, Any]:
        """Prepare a flag submission and return its human-approval digest."""
        return prepare_flag_submission(scope, flag=flag, target=target, team=team, endpoint=endpoint)

    @mcp.tool(name="koth_submit_flag")
    def koth_submit_flag(bundle: str, approval_digest: str) -> dict[str, Any]:
        """Submit only the exact flag bundle approved by its digest."""
        return submit_flag(scope, bundle, approval_digest)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the scoped OmniCTF HexStrike adapter")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    create_server(args.profile).run()


if __name__ == "__main__":
    main()
