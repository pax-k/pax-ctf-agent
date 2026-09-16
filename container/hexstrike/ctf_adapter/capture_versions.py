from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path("/opt/ctf-adapter")


def main() -> None:
    packages = subprocess.run(
        ["dpkg-query", "-W", "-f=${binary:Package}\t${Version}\n"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    (ROOT / "dpkg-versions.txt").write_text(packages, encoding="utf-8")

    freezes: list[str] = []
    for python in sorted(Path("/opt/ctf-venvs").glob("*/bin/python")):
        result = subprocess.run(
            [str(python), "-m", "pip", "freeze", "--all"],
            check=True,
            capture_output=True,
            text=True,
        )
        freezes.append(f"[{python.parents[1].name}]\n{result.stdout}")
    (ROOT / "python-versions.txt").write_text("\n".join(freezes), encoding="utf-8")

    registry = json.loads((ROOT / "tools.json").read_text(encoding="utf-8"))
    binaries = sorted({item["binary"] for item in registry["tools"]})
    lines = []
    for binary in binaries:
        result = subprocess.run(
            ["sh", "-c", 'command -v -- "$1"', "sh", binary],
            check=False,
            capture_output=True,
            text=True,
        )
        lines.append(f"{binary}\t{result.stdout.strip() if result.returncode == 0 else 'MISSING'}")
    (ROOT / "tool-smoke.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if any(line.endswith("\tMISSING") for line in lines):
        raise SystemExit("one or more declared tool binaries are missing")


if __name__ == "__main__":
    main()
