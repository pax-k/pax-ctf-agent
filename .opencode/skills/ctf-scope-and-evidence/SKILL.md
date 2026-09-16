---
name: ctf-scope-and-evidence
description: Validate OmniCTF written scope and maintain the cross-lane evidence index without changing finding ownership. Use when opening, closing, or reconciling an engagement lane.
license: Apache-2.0
---

# Validate scope and evidence

Treat `SCOPE.md` as the authority and `scope.json` as its machine-readable
enforcement input. The JSON file can narrow the written scope but cannot expand
it. Stop if target identity, authorization, time, account, source, or permitted
effect is inconsistent.

For each result, record the asset, lane, owner, tool or skill, timestamp,
validation state, evidence path, and source. Keep Strix, OpenCode, and
HexStrike evidence in their owner directories. Raw output is not a validated
finding. Record failed, partial, timed-out, and skipped work as such.

Before publishing a write-up, remove flags, credentials, personal data, and
private target details. Keep hashes and sanitized reproduction steps when they
are necessary to verify provenance.
