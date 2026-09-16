# Contributing

Contributions must preserve the authorization, lane-ownership, evidence, and
isolation rules in [AGENTS.md](./AGENTS.md) and the
[operating modes](./docs/opencode-operating-modes.md).

## Before a change

1. Do not add engagement scopes, credentials, logs, findings, or target data.
2. Record the requirement and the security boundary changed by the proposal.
3. Use exact upstream revisions for imported tools and skills.
4. Review new skill text for external endpoints, destructive actions, secret
   handling, persistence, and scope expansion.

## Validate a change

Run:

```bash
./scripts/validate-release.sh
```

The check needs Git, Python 3.10+, a C compiler, and Compose 2.24.4+. It does
not start the tool container. Gitleaks runs when installed; use
`./scripts/validate-release.sh --require-secrets` for a required secret scan.

For a container change, also build the image and inspect its inventory as
shown in [Getting started](./docs/getting-started.md). Record the tested
architecture. A successful build does not prove the MCP boundary or tool call.

## Change manifests and skills

- Edit `config/coverage.json`, then run `python3 scripts/generate-coverage.py`.
  Do not edit the generated coverage matrix directly.
- Keep tool registry names, server profiles, and MCP client allowlists aligned.
  `scripts/validate-manifests.py` checks these relationships.
- After reviewing a skill change, update its `config/skills.lock.json` entry.
  The content hash uses sorted relative file paths, a NUL separator after each
  path, and the corresponding file bytes. Use the `tree_hash` function in
  `scripts/validate-manifests.py`; do not change a hash merely to hide drift.
- Keep the upstream source, revision, license declaration, and local changes
  traceable in [third-party notices](./THIRD_PARTY_NOTICES.md).

## What the checks prove

Adapter tests exercise request boundaries and synthetic KOTH effects. Fixture
checks compile or inspect local samples; the Blockchain check currently looks
for source markers and does not compile EVM or Solana projects. Manifest checks
verify selected relationships, not full JSON Schema conformance. A passing
local check does not prove native tool behavior, provider access, or live-event
acceptance.

CI separately builds both native images, produces SPDX inventories, and uploads
Trivy reports. Trivy uses `exit-code: 0`; report findings require review even
when the workflow is green.

## Pull requests

Describe the behavior change, security impact, validation evidence, and any
unverified runtime or provider behavior. Do not attach private assessment
evidence to a public pull request.
