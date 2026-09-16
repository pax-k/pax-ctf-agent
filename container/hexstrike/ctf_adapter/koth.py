from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import display_path, input_path, output_path
from .scope import EngagementScope, ScopeError


class ApprovalError(ValueError):
    """Raised when a KOTH mutation is not tied to an approved digest."""


def snapshot(source: str, name: str) -> dict[str, Any]:
    started = datetime.now(timezone.utc)
    before = time.monotonic()
    source_path = input_path(source)
    destination = output_path(f"koth/snapshots/{_safe_name(name)}")
    if destination.exists():
        raise ApprovalError("snapshot destination already exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_path, destination, symlinks=True)
    return _result(
        "koth_snapshot",
        "completed",
        display_path(source_path),
        started,
        before,
        [path for path in destination.rglob("*") if path.is_file()],
        {"snapshot": display_path(destination)},
    )


def prepare_patch(scope: EngagementScope, patch_asset: str, checkout: str) -> dict[str, Any]:
    started = datetime.now(timezone.utc)
    before = time.monotonic()
    scope.require_category("koth")
    patch_path = input_path(patch_asset)
    checkout_path = output_path(checkout, must_exist=True)
    status = subprocess.run(
        ["git", "-C", str(checkout_path), "status", "--porcelain"],
        check=True,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if status.stdout:
        raise ApprovalError("KOTH checkout must be clean before patch preparation")
    base_head = subprocess.run(
        ["git", "-C", str(checkout_path), "rev-parse", "HEAD"],
        check=True,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=60,
    ).stdout.strip()
    check = subprocess.run(
        ["git", "-C", str(checkout_path), "apply", "--check", str(patch_path)],
        check=True,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=60,
    )
    bundle = {
        "action": "apply-patch",
        "engagementId": scope.engagement_id,
        "checkout": display_path(checkout_path),
        "patchAsset": display_path(patch_path),
        "patchSha256": _sha256(patch_path),
        "baseHead": base_head,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    digest = _digest(bundle)
    bundle["approvalDigest"] = digest
    bundle_path = output_path(f"koth/approvals/patch-{digest}.json")
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    validation_path = bundle_path.with_name(f"validation-{digest}.json")
    validation_path.write_text(
        json.dumps(
            {
                "validationState": "passed",
                "baseHead": base_head,
                "patchSha256": bundle["patchSha256"],
                "stdout": check.stdout,
                "stderr": check.stderr,
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    rollback_plan_path = bundle_path.with_name(f"rollback-plan-{digest}.json")
    rollback_plan_path.write_text(
        json.dumps(
            {
                "baseHead": base_head,
                "strategy": "A binary reverse patch is generated immediately after the approved apply.",
                "approvalDigest": digest,
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    return _result(
        "koth_prepare_patch",
        "approval_required",
        display_path(patch_path),
        started,
        before,
        [bundle_path, validation_path, rollback_plan_path],
        {
            "approvalDigest": digest,
            "bundle": display_path(bundle_path),
            "validationReport": display_path(validation_path),
            "rollbackPlan": display_path(rollback_plan_path),
        },
    )


def apply_patch(scope: EngagementScope, bundle: str, approval_digest: str) -> dict[str, Any]:
    started = datetime.now(timezone.utc)
    before = time.monotonic()
    if not scope.koth.get("allowPatchApplication", False):
        raise ScopeError("KOTH patch application is not authorized")
    bundle_path = output_path(bundle, must_exist=True)
    data = json.loads(bundle_path.read_text(encoding="utf-8"))
    _verify_bundle(data, approval_digest, "apply-patch", scope.engagement_id)
    checkout_path = output_path(_strip_output(data["checkout"]), must_exist=True)
    patch_path = input_path(_strip_input(data["patchAsset"]))
    if _sha256(patch_path) != data["patchSha256"]:
        raise ApprovalError("patch content changed after approval preparation")
    current_head = subprocess.run(
        ["git", "-C", str(checkout_path), "rev-parse", "HEAD"],
        check=True,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=60,
    ).stdout.strip()
    if current_head != data["baseHead"]:
        raise ApprovalError("KOTH checkout HEAD changed after patch preparation")

    status = subprocess.run(
        ["git", "-C", str(checkout_path), "status", "--porcelain"],
        check=True,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=60,
    )
    if status.stdout:
        raise ApprovalError("KOTH checkout changed after patch preparation")
    receipt_path = _claim_approval(bundle_path, "apply-patch", approval_digest)
    subprocess.run(
        ["git", "-C", str(checkout_path), "apply", str(patch_path)],
        check=True,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=60,
    )
    rollback_path = bundle_path.with_name(f"rollback-{approval_digest}.patch")
    rollback = subprocess.run(
        ["git", "-C", str(checkout_path), "diff", "--binary", "HEAD"],
        check=True,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=60,
    )
    rollback_path.write_bytes(rollback.stdout)
    return _result(
        "koth_apply_patch",
        "completed",
        display_path(bundle_path),
        started,
        before,
        [receipt_path, rollback_path],
        {
            "approvalDigest": approval_digest,
            "rollback": display_path(rollback_path),
            "rollbackCommand": ["git", "apply", "--reverse", display_path(rollback_path)],
        },
    )


def prepare_flag_submission(
    scope: EngagementScope, *, flag: str, target: str, team: str, endpoint: str
) -> dict[str, Any]:
    started = datetime.now(timezone.utc)
    before = time.monotonic()
    scope.require_category("koth")
    scope.require_target(endpoint)
    if endpoint not in scope.koth.get("submissionEndpoints", []):
        raise ScopeError("flag endpoint is not an authorized KOTH submission endpoint")
    submission = {
        "action": "submit-flag",
        "engagementId": scope.engagement_id,
        "flag": flag,
        "target": target,
        "team": team,
        "endpoint": endpoint,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    digest = _digest(submission)
    submission["approvalDigest"] = digest
    path = output_path(f"koth/approvals/flag-{digest}.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(submission, indent=2) + "\n", encoding="utf-8")
    return _result(
        "koth_prepare_flag_submission",
        "approval_required",
        target,
        started,
        before,
        [path],
        {"approvalDigest": digest, "bundle": display_path(path)},
    )


def submit_flag(scope: EngagementScope, bundle: str, approval_digest: str) -> dict[str, Any]:
    started = datetime.now(timezone.utc)
    before = time.monotonic()
    if not scope.koth.get("allowFlagSubmission", False):
        raise ScopeError("KOTH flag submission is not authorized")
    bundle_path = output_path(bundle, must_exist=True)
    data = json.loads(bundle_path.read_text(encoding="utf-8"))
    _verify_bundle(data, approval_digest, "submit-flag", scope.engagement_id)
    scope.require_target(data["endpoint"])
    if data["endpoint"] not in scope.koth.get("submissionEndpoints", []):
        raise ScopeError("flag endpoint is not an authorized KOTH submission endpoint")
    receipt_path = _claim_approval(bundle_path, "submit-flag", approval_digest)
    payload = json.dumps({key: data[key] for key in ("flag", "target", "team")}).encode()
    request = urllib.request.Request(
        data["endpoint"],
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        response_body = response.read(65536).decode("utf-8", errors="replace")
        status = response.status
    response_path = output_path(f"koth/responses/flag-{approval_digest}.txt")
    response_path.parent.mkdir(parents=True, exist_ok=True)
    response_path.write_text(response_body, encoding="utf-8")
    return _result(
        "koth_submit_flag",
        "completed" if 200 <= status < 300 else "failed",
        data["target"],
        started,
        before,
        [receipt_path, response_path],
        {
            "approvalDigest": approval_digest,
            "httpStatus": status,
            "responsePath": display_path(response_path),
        },
        exit_code=0 if 200 <= status < 300 else 1,
    )


def _verify_bundle(
    data: dict[str, Any], approval_digest: str, action: str, engagement_id: str
) -> None:
    if data.get("action") != action:
        raise ApprovalError("approval bundle has the wrong action")
    if data.get("engagementId") != engagement_id:
        raise ApprovalError("approval bundle belongs to another engagement")
    expected = data.pop("approvalDigest", None)
    try:
        actual = _digest(data)
    finally:
        if expected is not None:
            data["approvalDigest"] = expected
    if expected != actual or approval_digest != actual:
        raise ApprovalError("approval digest does not match the exact prepared action")


def _claim_approval(bundle_path: Path, action: str, approval_digest: str) -> Path:
    receipt = bundle_path.with_name(f"consumed-{action}-{approval_digest}.json")
    payload = json.dumps(
        {
            "action": action,
            "approvalDigest": approval_digest,
            "consumedAt": datetime.now(timezone.utc).isoformat(),
        },
        indent=2,
    ) + "\n"
    try:
        descriptor = os.open(receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ApprovalError("approval digest was already consumed") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as destination:
        destination.write(payload)
    return receipt


def _result(
    tool: str,
    validation_state: str,
    asset: str,
    started: datetime,
    before: float,
    artifacts: list[Path],
    details: dict[str, Any],
    *,
    exit_code: int = 0,
) -> dict[str, Any]:
    run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}-{tool}-{uuid.uuid4().hex[:8]}"
    run_dir = output_path(f"evidence/{run_id}")
    run_dir.mkdir(parents=True, exist_ok=False)
    stdout_path = run_dir / "stdout.txt"
    stderr_path = run_dir / "stderr.txt"
    stdout_path.write_text("", encoding="utf-8")
    stderr_path.write_text("", encoding="utf-8")
    existing_artifacts = [path for path in artifacts if path.is_file()]
    result = {
        "tool": tool,
        "toolVersion": "1.0.0",
        "category": "koth",
        "asset": asset,
        "commandSummary": [f"internal:{tool}"],
        "startedAt": started.isoformat(),
        "durationMs": int((time.monotonic() - before) * 1000),
        "exitCode": exit_code,
        "timedOut": False,
        "stdoutPath": display_path(stdout_path),
        "stderrPath": display_path(stderr_path),
        "createdArtifacts": [display_path(path) for path in existing_artifacts],
        "artifactHashes": {display_path(path): _sha256(path) for path in existing_artifacts},
        "validationState": validation_state,
        "details": details,
    }
    (run_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def _digest(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_name(name: str) -> str:
    if not name or any(character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-" for character in name):
        raise ApprovalError("name contains unsupported characters")
    return name


def _strip_input(value: str) -> str:
    if not value.startswith("input/"):
        raise ApprovalError("bundle input path is invalid")
    return value[len("input/"):]


def _strip_output(value: str) -> str:
    if not value.startswith("output/"):
        raise ApprovalError("bundle output path is invalid")
    return value[len("output/"):]
