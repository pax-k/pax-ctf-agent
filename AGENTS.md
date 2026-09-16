# Authorized Security Operations

Use this project only for systems covered by written authorization. Read
`docs/opencode-operating-modes.md` before starting an assessment.

## Select one operating mode

State the selected mode before any active security test.

- **Mode 1 — OpenCode orchestrates:** OpenCode selects and sequences independent
  lanes. Strix owns application, API, source, LLM, AWS, Kubernetes, and Active
  Directory testing inside each Strix run. OpenCode can call HexStrike directly
  only for a documented gap. Do not connect that Strix run to HexStrike.
- **Mode 2 — Strix orchestrates:** Strix owns the assessment. A legacy HexStrike
  connection requires a separately reviewed narrow profile; the bundled CTF
  adapter supports Mode 1 only. OpenCode must keep its HexStrike MCP disabled.
  OpenCode can run the installed mobile or CI/CD skills as separate lanes before
  or after Strix, not concurrently against the same surface.

If the mode is not stated, use Mode 1. Keep every HexStrike MCP server disabled
until one non-Web category lane is selected. Mode 2 is an explicit legacy
choice for an application-only assessment.

## Lane ownership

- Strix owns web, API, application source, LLM application, offensive AWS,
  Kubernetes, Active Directory, dependency CVE, exploit validation, coverage,
  and its report.
- The installed mobile skills own Android and iOS source or artifact review.
- The installed CI/CD skills own GitHub Actions workflow review.
- HexStrike owns execution for one explicitly selected Reverse, PWN,
  Forensics, Crypto, OSINT, Blockchain, Misc, or KOTH profile. It is an
  executor, not a planner or report authority.
- OpenCode owns scope routing and the cross-lane evidence index. It must preserve
  the original source of every finding.

Do not run two planners or two scanners against the same surface for coverage
alone. Do not let OpenCode and Strix connect to the same HexStrike server during
one lane.

## Safety boundary

- Confirm the authorized target, assets, accounts, time window, and prohibited
  actions before active testing.
- Use static review or a synthetic canary before a destructive or externally
  visible proof.
- Never exfiltrate real secrets, retain credentials, install persistence, delete
  evidence or logs, deny service, or affect third-party systems.
- Treat offensive payloads in third-party skills as threat-model examples. Do
  not execute them outside a disposable lab unless the user explicitly
  authorizes that exact proof and target.
- Run HexStrike only through `compose.hexstrike.yml`. Do not give it the Docker
  socket, mounts other than the documented read-only input and writable output
  workbench, host networking, `--privileged`, or persistent credentials. Full
  outbound bridge networking does not grant scope authority.
- Stop when scope, authorization, target identity, or impact is uncertain.

## Evidence contract

Keep outputs separate by owner:

```text
engagements/<id>/
  SCOPE.md
  strix-instructions.md
  evidence/
    strix/
    opencode-mobile/
    opencode-cicd/
    opencode-ctf/
    hexstrike/
    koth/
  INDEX.md
```

For each result, record the asset, lane, tool or skill, timestamp, validation
state, evidence path, and source. Do not label raw HexStrike output as a
Strix-validated finding.
