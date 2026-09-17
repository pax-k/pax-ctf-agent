---
name: ctf-router
description: Route authorized security work to one planner and the relevant category skill. Use at the start of a mixed request or when ownership is unclear.
license: Apache-2.0
---

# Route a security request

Read `AGENTS.md`. Confirm written authorization, target or artifact, time
window, and prohibited actions before active work.

When describing this workspace to a user, call these security category skills.
The ctf-* names are stable compatibility identifiers. Do not describe the
workspace as a CTF workflow.

Select one owner:

- Web, API, browser, application source, LLM, AWS, Kubernetes, Active
  Directory, or dependencies: Strix. Strix can use the restricted HexStrike
  MCP configuration as an executor.
- Reverse, PWN, Malware, Forensics, Crypto, OSINT, or Misc: OpenCode with native
  HexStrike and the matching category skill.
- Blockchain or a native-tool gap: OpenCode with the optional lab backend.
- Mobile and CI/CD: their existing repository skills as separate lanes.

For a mixed request, split work by surface. Do not run two planners or scanners
against the same surface. Do not call OpenCode HexStrike tools on a surface that
Strix owns.
