from __future__ import annotations

import ipaddress
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


class ScopeError(ValueError):
    """Raised when a network target is not in the written engagement scope."""


@dataclass(frozen=True)
class EngagementScope:
    engagement_id: str
    categories: frozenset[str]
    targets: tuple[str, ...]
    osint_sources: tuple[str, ...]
    koth: dict[str, object]
    starts_at: datetime | None = None
    ends_at: datetime | None = None

    @classmethod
    def load(cls, path: str | Path | None = None) -> "EngagementScope":
        scope_path = Path(path or os.environ.get("CTF_SCOPE_FILE", "/workbench/input/scope.json"))
        data = json.loads(scope_path.read_text(encoding="utf-8"))
        if data.get("mode") != "mode-1-opencode-orchestrates":
            raise ScopeError("the CTF adapter requires Mode 1")
        engagement_id = str(data.get("engagementId", ""))
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,63}", engagement_id):
            raise ScopeError("engagementId does not match the scope contract")
        starts_at = _parse_datetime(data.get("startsAt"), "startsAt")
        ends_at = _parse_datetime(data.get("endsAt"), "endsAt")
        if ends_at <= starts_at:
            raise ScopeError("scope endsAt must be after startsAt")
        return cls(
            engagement_id=engagement_id,
            categories=frozenset(str(value) for value in data["categories"]),
            targets=tuple(str(value) for value in data["targets"]),
            osint_sources=tuple(str(value) for value in data["osintSources"]),
            koth=dict(data["koth"]),
            starts_at=starts_at,
            ends_at=ends_at,
        )

    def require_category(self, category: str) -> None:
        self._require_active()
        if category not in self.categories:
            raise ScopeError(f"category is not authorized: {category}")

    def require_target(self, target: str, *, osint: bool = False) -> str:
        self._require_active()
        host = _extract_host(target)
        allowed = self.osint_sources if osint else self.targets
        if not any(_matches(host, rule) for rule in allowed):
            raise ScopeError(f"target is outside the engagement scope: {host}")
        return target

    def require_subject(self, subject: str) -> str:
        self._require_active()
        value = subject.strip()
        if not value or value not in self.targets:
            raise ScopeError("subject is outside the engagement scope")
        return value

    def _require_active(self) -> None:
        if self.starts_at is None or self.ends_at is None:
            return
        now = datetime.now(timezone.utc)
        if not self.starts_at <= now <= self.ends_at:
            raise ScopeError("the engagement scope is outside its authorized time window")


def _parse_datetime(value: object, field: str) -> datetime:
    if not isinstance(value, str):
        raise ScopeError(f"scope {field} must be a date-time string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ScopeError(f"scope {field} is not a valid date-time") from exc
    if parsed.tzinfo is None:
        raise ScopeError(f"scope {field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _extract_host(target: str) -> str:
    value = target.strip()
    parsed = urlparse(value if "://" in value else f"//{value}")
    host = parsed.hostname
    if not host:
        raise ScopeError("target must contain a valid hostname or IP address")
    return host.rstrip(".").lower()


def _matches(host: str, rule: str) -> bool:
    normalized = rule.strip().rstrip(".").lower()
    parsed = urlparse(normalized if "://" in normalized else f"//{normalized}")
    rule_host = parsed.hostname or normalized

    if rule_host.startswith("*."):
        suffix = rule_host[1:]
        return host.endswith(suffix) and host != suffix[1:]

    try:
        network = ipaddress.ip_network(rule_host, strict=False)
        return ipaddress.ip_address(host) in network
    except ValueError:
        return host == rule_host
