#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test_dir=$(mktemp -d "${TMPDIR:-/tmp}/hacking-workshop-native.XXXXXX")

cleanup() {
  if [ -f "$test_dir/.hexstrike/native/native.pid" ]; then
    test_pid=$(cat "$test_dir/.hexstrike/native/native.pid")
    kill "$test_pid" 2>/dev/null || true
  fi
  rm -rf "$test_dir"
}
trap cleanup EXIT HUP INT TERM

tar -C "$repo_dir" \
  --exclude=.git \
  --exclude=.hexstrike \
  --exclude=strix_runs \
  --exclude=engagements \
  --exclude=workbench/output \
  -cf - . | tar -C "$test_dir" -xf -

"$test_dir/scripts/setup"
HEXSTRIKE_PORT=18888 "$test_dir/scripts/start-hexstrike"

HEXSTRIKE_PORT=18888 "$test_dir/.hexstrike/native/venv/bin/python" - "$test_dir/scripts/hexstrike-mcp" <<'PY'
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    parameters = StdioServerParameters(
        command=sys.argv[1], args=[], env={"HEXSTRIKE_PORT": "18888"}
    )
    async with stdio_client(parameters) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            assert any(tool.name == "server_health" for tool in tools)
            result = await session.call_tool("server_health", {})
            assert not result.isError


asyncio.run(main())
PY

printf '%s\n' 'fresh native setup and read-only MCP health call passed'
