#!/bin/sh
set -eu

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

require_secrets=false
case "${1:-}" in
  '') ;;
  --require-secrets) require_secrets=true ;;
  *) fail 'usage: ./scripts/validate-release.sh [--require-secrets]' ;;
esac
test "$#" -le 1 || fail 'usage: ./scripts/validate-release.sh [--require-secrets]'
if [ "$require_secrets" = true ]; then
  command -v gitleaks >/dev/null 2>&1 || fail 'gitleaks is required for publication checks'
fi

for command_name in git python3 docker cc; do
  command -v "${command_name}" >/dev/null 2>&1 \
    || fail "required command is unavailable: ${command_name}"
done

python3 - <<'PY'
import json
import subprocess
from pathlib import Path

# Validate the public file set, not ignored private engagement or runtime data.
output = subprocess.check_output([
    "git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"
])
for name in output.split(b"\0"):
    if name and name.endswith(b".json"):
        path = Path(name.decode("utf-8"))
        with path.open(encoding="utf-8") as source:
            json.load(source)
print("public JSON syntax: passed")
PY

find scripts container -type f -name '*.sh' -print \
  | while IFS= read -r shell_file; do
      sh -n "${shell_file}"
    done

python3 scripts/validate-manifests.py
python3 scripts/generate-coverage.py --check
PYTHONPATH=container/hexstrike python3 -m unittest discover -s tests
./scripts/test-fixtures.sh all

docker compose -f compose.hexstrike.yml config --quiet
docker compose -f compose.hexstrike.yml -f compose.hexstrike.offline.yml config --quiet

python3 - <<'PY'
import json
import subprocess


def compose(*files):
    command = ["docker", "compose"]
    for file_name in files:
        command.extend(["-f", file_name])
    command.extend(["config", "--format", "json"])
    return json.loads(subprocess.run(command, check=True, capture_output=True, text=True).stdout)


online = compose("compose.hexstrike.yml")
service = online["services"]["hexstrike"]
assert service["read_only"] is True
assert service.get("privileged", False) is False
assert service["cap_drop"] == ["ALL"]
assert "NET_ADMIN" in service["cap_add"] and "NET_RAW" in service["cap_add"]
assert service.get("network_mode") != "host"
assert all("docker.sock" not in json.dumps(mount) for mount in service["volumes"])

mounts = {mount["target"]: mount for mount in service["volumes"]}
assert set(mounts) == {"/workbench/input", "/workbench/output"}
assert mounts["/workbench/input"]["read_only"] is True
assert mounts["/workbench/output"].get("read_only", False) is False

offline = compose("compose.hexstrike.yml", "compose.hexstrike.offline.yml")
assert not offline["services"]["hexstrike"].get("ports"), "offline mode publishes host ports"
offline_networks = set(offline["services"]["hexstrike"]["networks"])
assert offline_networks == {"hexstrike-offline"}
assert offline["networks"]["hexstrike-offline"]["internal"] is True

config = json.load(open("opencode.json", encoding="utf-8"))
assert config["permission"]["hexstrike_*"] == "deny"
assert all(server["enabled"] is False for server in config["mcp"].values())
print("container and OpenCode policy: passed")
PY

python3 - <<'PY'
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

root = Path.cwd()
missing = []
candidate_output = subprocess.run(
    ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
    check=True,
    capture_output=True,
).stdout
candidate_paths = [root / Path(path.decode("utf-8")) for path in candidate_output.split(b"\0") if path]

for document in (path for path in candidate_paths if path.suffix == ".md"):
    text = document.read_text(encoding="utf-8")
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).strip().split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if not target.startswith(("./", "../")) and Path(target).suffix not in {
            ".json", ".md", ".sh", ".yml", ".yaml"
        }:
            continue
        resolved = (document.parent / unquote(target)).resolve()
        if not resolved.exists():
            missing.append(f"{document.relative_to(root)} -> {target}")

if missing:
    raise SystemExit("missing local Markdown links:\n" + "\n".join(missing))
print("local Markdown links: passed")
PY

for private_path in \
  discussion.md \
  hexstrike.log \
  hexstrike-localhost.patch \
  engagements/private-example/SCOPE.md \
  engagements/private-example/strix-instructions.md \
  workbench/input/private.bin \
  workbench/output/evidence.json
do
  git check-ignore --quiet "${private_path}" \
    || fail "private path is not ignored: ${private_path}"
done

git check-ignore --quiet engagements/example/SCOPE.md \
  && fail "sanitized engagement example is ignored"
git check-ignore --quiet workbench/input/.gitkeep \
  && fail "input workbench marker is ignored"
git check-ignore --quiet workbench/output/.gitkeep \
  && fail "output workbench marker is ignored"

test -f LICENSE || fail "root Apache-2.0 license is missing"

# An ignore rule cannot protect a file that is already tracked.
if [ -n "$(git ls-files --cached --ignored --exclude-standard)" ]; then
  fail 'tracked files match ignore rules; review the index before publication'
fi

if command -v gitleaks >/dev/null 2>&1; then
  python3 - <<'PY'
import shutil
import subprocess
import tempfile
from pathlib import Path

root = Path.cwd()
candidate_output = subprocess.run(
    ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
    check=True,
    capture_output=True,
).stdout
with tempfile.TemporaryDirectory(prefix="hacking-workshop-release-") as scan_directory:
    scan_root = Path(scan_directory)
    for raw_path in candidate_output.split(b"\0"):
        if not raw_path:
            continue
        relative_path = Path(raw_path.decode("utf-8"))
        source = root / relative_path
        destination = scan_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    subprocess.run(["gitleaks", "dir", str(scan_root), "--no-banner", "--redact"], check=True)
PY
  printf '%s\n' 'secret scan: passed'
else
  printf '%s\n' 'WARNING: gitleaks is unavailable; secret scan was not run' >&2
fi

printf '%s\n' 'local validation: passed (container builds and live targets are separate checks)'
