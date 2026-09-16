# OpenCode, Strix, Skills, and HexStrike

State one operating mode before active security work. Mode 1 is the default for
OmniCTF.

## Shared prerequisites

1. Copy `engagements/example/` to a new private `engagements/<id>/` directory.
   Complete `SCOPE.md`, `scope.json`, and `INDEX.md`; the example scope is inactive.
2. Record targets, accounts, time, allowed OSINT sources, prohibited actions,
   KOTH policy, and stop conditions.
3. Copy the approved `scope.json` to `workbench/input/scope.json`.
4. Keep all HexStrike MCP entries disabled until a category lane is selected.
5. Keep evidence separated by owner.

## Mode 1: OpenCode orchestrates

Use Mode 1 for OmniCTF and every multi-category engagement.

### Ownership

- OpenCode owns category routing, lane order, budgets, and `INDEX.md`.
- Strix owns Web and application assessment and its report.
- HexStrike executes one selected Reverse, PWN, Forensics, Crypto, OSINT,
  Blockchain, Misc, or KOTH profile.
- Mobile and CI/CD skills remain separate lanes.

### Run sequence

1. Load `ctf-router` and `ctf-scope-and-evidence`.
2. Record one lane, owner, target or artifact, and expected output in `INDEX.md`.
3. For Web, load `ctf-web` and the Strix skill. Run Strix without HexStrike.
4. For another category, load its skill and enable only the matching
   `hexstrike_<category>` MCP entry.
5. Start the isolated service and call only tools registered by that profile.
6. Inspect the structured result and complete evidence. Record failures and
   timeouts; do not convert raw output into a finding.
7. Disable the MCP entry and close the lane before selecting another profile.

The Web gap profile is exceptional. Before enabling it, record the exact Strix
capability gap in `INDEX.md`. Do not use it for duplicate scanning.

## Mode 2: Strix orchestrates

Use Mode 2 only when the user explicitly requests an application-only Strix
assessment. Strix owns planning, execution, coverage, findings, and reporting.
OpenCode keeps all local HexStrike MCP entries disabled.

Do not attach the expanded CTF profiles to Strix. If the application assessment
finds a binary or artifact gap, complete the Strix lane, then open a separate
Mode 1 lane for the appropriate CTF profile.

The bundled adapter and `scope.json` contract support Mode 1 only. Mode 2 does
not have a ready-to-use HexStrike connection in this repository. Any legacy
Strix connection needs its own reviewed configuration and scope.

## Enforcement and limits

- `AGENTS.md` defines routing and safety rules.
- `contracts/scope.schema.json` defines the scope format. The adapter checks
  selected fields, the time window, category, and requested targets. It does
  not invoke a full JSON Schema validator.
- `opencode.json` keeps every MCP server disabled and requires approval for
  HexStrike tools.
- Category MCP files and server-side profile registration restrict tool names.
- `compose.hexstrike.yml` restricts capabilities, ports, and mounts.
- The adapter validates paths, symlinks, scope, options, time, process count,
  file size, and structured evidence output.
- KOTH digests bind human approval to one exact mutation.

The boundaries have these limits:

- `AGENTS.md` and skill instructions are operator rules, not executable access
  controls. The client must obtain human consent for each KOTH effect. A digest
  binds content and prevents replay; it cannot prove who approved the action.
- Target checks compare the requested host or subject with scope entries.
  They do not enforce an outbound firewall, resolve DNS destinations, or inspect
  redirects and all network calls made by a child tool.
- The base Compose network permits outbound access. The offline override
  replaces it with an internal network and removes published ports. This is
  container isolation, not a complete sandbox for arbitrary hostile code.
- The upstream HexStrike HTTP API remains a separate interface on loopback in
  the base configuration. Adapter scope checks do not protect that API.
- A completed tool process is not a validated finding. Preserve the complete
  output and record the separate validation decision in the evidence index.

These controls do not grant authorization or prevent direct use of other host
tools. Stop when written scope, target identity, or impact is not clear.
