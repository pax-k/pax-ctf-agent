from __future__ import annotations

import hashlib
import json
import os
import re
import resource
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import OUTPUT_ROOT, display_path, input_path, output_path
from .scope import EngagementScope


class ToolContractError(ValueError):
    """Raised when a tool request violates its declared contract."""


@dataclass(frozen=True)
class ToolSpec:
    name: str
    category: str
    binary: str
    version: str
    kind: str
    args: tuple[str, ...]
    timeout: int
    options: dict[str, dict[str, Any]]
    cpu_seconds: int = 900
    memory_mib: int = 8192
    output_mib: int = 512
    processes: int = 512

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolSpec":
        return cls(
            name=data["name"],
            category=data["category"],
            binary=data["binary"],
            version=data["version"],
            kind=data["kind"],
            args=tuple(data.get("args", [])),
            timeout=int(data.get("timeout", 120)),
            options=dict(data.get("options", {})),
            cpu_seconds=int(data.get("cpuSeconds", min(int(data.get("timeout", 120)), 900))),
            memory_mib=int(data.get("memoryMiB", 8192)),
            output_mib=int(data.get("outputMiB", 512)),
            processes=int(data.get("processes", 512)),
        )


def load_registry(path: str | Path) -> dict[str, ToolSpec]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    specs = [ToolSpec.from_dict(item) for item in data["tools"]]
    if len(specs) != len({spec.name for spec in specs}):
        raise ToolContractError("tool registry contains duplicate names")
    return {spec.name: spec for spec in specs}


class ToolRunner:
    def __init__(self, scope: EngagementScope, lane: str):
        self.scope = scope
        self.lane = "web" if lane == "web-gap" else lane

    def run(
        self,
        spec: ToolSpec,
        *,
        asset: str = "",
        target: str = "",
        output_name: str = "",
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.scope.require_category(self.lane)
        resolved_asset: Path | None = None
        checked_target = ""
        if spec.kind in {"artifact", "script", "project"}:
            resolved_asset = input_path(asset)
        elif spec.kind in {"target", "osint"}:
            checked_target = self.scope.require_target(target)
        elif spec.kind == "osint_source":
            checked_target = self.scope.require_target(target, osint=True)
        elif spec.kind == "subject":
            checked_target = self.scope.require_subject(target)
        elif spec.kind != "local":
            raise ToolContractError(f"unknown tool kind: {spec.kind}")

        run_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{spec.name}-{uuid.uuid4().hex[:8]}"
        run_dir = output_path(f"evidence/{run_id}")
        run_dir.mkdir(parents=True, exist_ok=False)
        if spec.kind == "project":
            staged_asset = run_dir / "project"
            if resolved_asset is None:
                raise ToolContractError("project tool requires an input asset")
            import shutil

            if resolved_asset.is_dir():
                shutil.copytree(resolved_asset, staged_asset, symlinks=True)
            else:
                staged_asset.mkdir()
                shutil.copy2(resolved_asset, staged_asset / resolved_asset.name)
                staged_asset = staged_asset / resolved_asset.name
            resolved_asset = staged_asset
        requested_output = run_dir / "artifacts"
        if output_name:
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", output_name):
                raise ToolContractError("output_name contains unsupported characters")
            requested_output = run_dir / output_name
        requested_output.mkdir(parents=True, exist_ok=True)

        values = {
            "asset": str(resolved_asset or ""),
            "target": checked_target,
            "output": str(requested_output),
        }
        argv = [spec.binary, *(_render(value, values) for value in spec.args)]
        argv.extend(_render_options(spec.options, options or {}))

        stdout_path = run_dir / "stdout.txt"
        stderr_path = run_dir / "stderr.txt"
        started = datetime.now(timezone.utc)
        before = time.monotonic()
        timed_out = False
        exit_code: int | None = None

        try:
            with stdout_path.open("wb") as stdout_file, stderr_path.open("wb") as stderr_file:
                completed = subprocess.run(
                    argv,
                    cwd=resolved_asset if spec.kind == "project" and resolved_asset.is_dir() else run_dir,
                    stdin=subprocess.DEVNULL,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    check=False,
                    timeout=min(spec.timeout, 900),
                    env=_bounded_environment(),
                    preexec_fn=lambda: _resource_limits(spec),
                )
                exit_code = completed.returncode
        except subprocess.TimeoutExpired:
            timed_out = True

        artifacts = [
            path for path in run_dir.rglob("*")
            if path.is_file() and path not in {stdout_path, stderr_path}
        ]
        result = {
            "tool": spec.name,
            "toolVersion": _detected_version(spec),
            "category": self.lane,
            "asset": display_path(resolved_asset) if resolved_asset else checked_target,
            "commandSummary": _redacted_argv(argv),
            "startedAt": started.isoformat(),
            "durationMs": int((time.monotonic() - before) * 1000),
            "exitCode": exit_code,
            "timedOut": timed_out,
            "stdoutPath": display_path(stdout_path),
            "stderrPath": display_path(stderr_path),
            "createdArtifacts": [display_path(path) for path in artifacts],
            "artifactHashes": {display_path(path): _sha256(path) for path in artifacts},
            "validationState": "timed_out" if timed_out else ("completed" if exit_code == 0 else "failed"),
        }
        (run_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return result


def _render(value: str, values: dict[str, str]) -> str:
    try:
        return value.format_map(values)
    except KeyError as exc:
        raise ToolContractError(f"unknown argument template: {exc.args[0]}") from exc


def _render_options(definitions: dict[str, dict[str, Any]], supplied: dict[str, Any]) -> list[str]:
    unknown = set(supplied) - set(definitions)
    if unknown:
        raise ToolContractError(f"unsupported options: {', '.join(sorted(unknown))}")
    rendered: list[str] = []
    for name, value in supplied.items():
        rule = definitions[name]
        option_type = rule.get("type", "string")
        if option_type == "integer":
            if isinstance(value, bool) or not isinstance(value, int):
                raise ToolContractError(f"option {name} must be an integer")
            if not int(rule.get("minimum", value)) <= value <= int(rule.get("maximum", value)):
                raise ToolContractError(f"option {name} is outside its allowed range")
        elif option_type == "enum":
            if value not in rule.get("values", []):
                raise ToolContractError(f"option {name} is not an allowed value")
        elif option_type == "boolean":
            if not isinstance(value, bool):
                raise ToolContractError(f"option {name} must be a boolean")
            if not value:
                continue
            value = None
        elif not isinstance(value, str) or len(value) > int(rule.get("maxLength", 200)):
            raise ToolContractError(f"option {name} must be a bounded string")
        rendered.append(str(rule["flag"]))
        if value is not None:
            rendered.append(str(value))
    return rendered


def _bounded_environment() -> dict[str, str]:
    allowed = {"HOME", "PATH", "LANG", "LC_ALL", "TERM", "RUST_BACKTRACE"}
    environment = {key: value for key, value in os.environ.items() if key in allowed}
    environment["HOME"] = os.environ.get("HOME", "/workspace/home")
    return environment


def _resource_limits(spec: ToolSpec) -> None:
    cpu_seconds = max(1, min(spec.cpu_seconds, 900))
    output_bytes = max(1, min(spec.output_mib, 512)) * 1024 * 1024
    memory_bytes = max(64, min(spec.memory_mib, 16384)) * 1024 * 1024
    processes = max(1, min(spec.processes, 512))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
    resource.setrlimit(resource.RLIMIT_FSIZE, (output_bytes, output_bytes))
    if sys.platform.startswith("linux"):
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
    resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))
    resource.setrlimit(resource.RLIMIT_NPROC, (processes, processes))


def _redacted_argv(argv: list[str]) -> list[str]:
    redacted: list[str] = []
    for value in argv:
        value = value.replace(str(Path("/workbench/input")), "input")
        value = value.replace(str(Path("/workbench/output")), "output")
        redacted.append(value[:500])
    return redacted


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _detected_version(spec: ToolSpec) -> str:
    if spec.version != "runtime":
        return spec.version
    try:
        completed = subprocess.run(
            [spec.binary, "--version"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            check=False,
            timeout=5,
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return "runtime-version-unavailable"
    output = (completed.stdout or completed.stderr).strip().splitlines()
    return output[0][:200] if output else "runtime-version-unavailable"
