#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {"reverse", "web", "forensics", "pwn", "crypto", "osint", "blockchain", "misc", "koth"}


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def tree_hash(directory: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in directory.rglob("*") if item.is_file()):
        digest.update(str(path.relative_to(directory)).encode() + b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> None:
    registry = load("container/hexstrike/tools.json")
    profiles = load("container/hexstrike/profiles.json")["profiles"]
    coverage = load("config/coverage.json")["capabilities"]
    skill_lock = load("config/skills.lock.json")["skills"]
    load("config/toolchain.lock.json")
    load("engagements/example/scope.json")
    load("opencode.json")

    tools = {item["name"]: item for item in registry["tools"]}
    assert len(tools) == len(registry["tools"]), "duplicate tool registry name"
    assert "gdb_peda_debug" not in tools, "PEDA tool remains in registry"
    assert "gdb_pwndbg_debug" in tools, "pwndbg replacement is missing"

    for profile, names in profiles.items():
        assert len(names) == len(set(names)), f"duplicate tool in profile {profile}"
        if profile != "koth":
            missing = set(names) - set(tools)
            assert not missing, f"profile {profile} has unknown tools: {sorted(missing)}"
        profile_path = ROOT / ("mcp-servers.hexstrike.json" if profile == "catalog" else f"mcp-servers.hexstrike.{profile}.json")
        config = json.loads(profile_path.read_text(encoding="utf-8"))[0]
        assert config["allowed_tools"] == ["tool_inventory", *names], f"MCP profile drift: {profile}"
        assert config["args"][-1] == profile, f"MCP command profile mismatch: {profile}"

    seen_categories = {item["category"] for item in coverage}
    assert seen_categories == CATEGORIES, f"coverage categories differ: {sorted(CATEGORIES - seen_categories)}"
    for capability in coverage:
        fixture = ROOT / capability["fixture"]
        assert fixture.exists(), f"missing fixture: {fixture}"
        skill = ROOT / ".opencode/skills" / capability["skill"] / "SKILL.md"
        assert skill.exists(), f"missing skill: {skill}"
        profile = capability["profile"]
        if profile:
            assert profile in profiles, f"unknown coverage profile: {profile}"
        mcp_tool = capability["mcpTool"]
        if mcp_tool:
            assert mcp_tool in profiles[profile], f"coverage tool not in profile: {mcp_tool}"
        assert not (capability["evidenceOwner"] == "strix" and capability["owner"] == "hexstrike"), "HexStrike evidence cannot be owned by Strix"

    locked_names = set()
    for entry in skill_lock:
        assert entry["name"] not in locked_names, f"duplicate skill lock: {entry['name']}"
        locked_names.add(entry["name"])
        directory = ROOT / ".opencode/skills" / entry["name"]
        assert directory.exists(), f"locked skill is missing: {entry['name']}"
        actual = tree_hash(directory)
        assert actual == entry["contentHash"], f"skill hash changed: {entry['name']}"

    assert "solve-challenge" not in locked_names, "broad solve-challenge skill must not be vendored"
    installed_names = {path.parent.name for path in (ROOT / ".opencode/skills").glob("*/SKILL.md")}
    assert installed_names == locked_names, f"skill lock coverage differs: {sorted(installed_names ^ locked_names)}"

    example = load("engagements/example/scope.json")
    assert example["targets"] == [] and example["osintSources"] == [], "public example grants network access"
    assert example["categories"] == [], "public example grants a category"
    assert example["koth"]["allowPatchApplication"] is False, "public example permits patch effects"
    assert example["koth"]["allowFlagSubmission"] is False, "public example permits flag effects"
    assert example["koth"]["submissionEndpoints"] == [], "public example has submission endpoints"
    print("manifest contracts: passed")


if __name__ == "__main__":
    main()
