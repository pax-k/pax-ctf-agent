#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_dir"

for script in scripts/check.sh scripts/doctor scripts/hexstrike-lab-mcp scripts/hexstrike-mcp scripts/run-strix scripts/setup scripts/start-hexstrike; do
  sh -n "$script"
done
python3 -m py_compile scripts/hexstrike-server.py

for json_file in opencode.json config/toolchain.lock.json config/strix-hexstrike.json extras/hexstrike-lab/image/profiles.json extras/hexstrike-lab/image/tools.json; do
  python3 -m json.tool "$json_file" >/dev/null
done

python3 - <<'PY'
import json
from pathlib import Path

profiles = json.loads(Path("extras/hexstrike-lab/image/profiles.json").read_text())
assert set(profiles) == {"version", "profiles"}
assert set(profiles["profiles"]) == {
    "reverse", "pwn", "forensics", "crypto", "osint", "blockchain", "misc", "lab"
}
assert not any("koth" in tool for tools in profiles["profiles"].values() for tool in tools)

native_tools = {
    "server_health", "httpx_probe", "wafw00f_scan", "api_schema_analyzer",
    "api_fuzzer", "graphql_scanner", "jwt_analyzer", "checkov_iac_scan",
    "trivy_scan", "kube_bench_cis", "prowler_scan", "scout_suite_assessment",
    "cloudmapper_analysis",
}
strix = json.loads(Path("config/strix-hexstrike.json").read_text())
assert len(strix) == 1
assert set(strix[0]["allowed_tools"]) <= native_tools
assert strix[0]["name"] == "hexstrike"
PY

if command -v opencode >/dev/null 2>&1; then
  opencode debug config >/dev/null
fi

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  docker compose -f extras/hexstrike-lab/compose.yml config --quiet
fi

if git ls-files engagements | grep -q .; then
  printf '%s\n' 'engagement files must not be tracked' >&2
  exit 1
fi

if rg -n 'hexstrike_koth|ctf-koth|KOTH' AGENTS.md README.md CONTRIBUTING.md docs config opencode.json; then
  printf '%s\n' 'obsolete CTF workflow text remains in the active project surface' >&2
  exit 1
fi

printf '%s\n' 'configuration checks passed'
