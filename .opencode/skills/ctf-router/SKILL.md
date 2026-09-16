---
name: ctf-router
description: Route an authorized CTF task to exactly one OmniCTF category owner and narrow HexStrike profile. Use at the start of a multi-category challenge or when ownership is unclear.
license: Apache-2.0
---

# Route an OmniCTF challenge

Read `AGENTS.md`, the engagement `SCOPE.md`, and its `scope.json`. State Mode 1
before active work. Reject a category, target, time, or action that the scope
does not authorize.

Select one owner:

- Web, API, browser, application source, LLM, AWS, Kubernetes, or Active
  Directory: Strix, without HexStrike.
- Reverse, PWN, Forensics, Crypto, OSINT, Blockchain, Misc, or KOTH: OpenCode
  with the matching narrow HexStrike profile and category skill.
- Mobile and CI/CD: their existing repository skills as separate lanes.

Do not run two planners or scanners against the same surface for coverage.
Record the lane, owner, profile, artifact or target, and expected evidence in
`INDEX.md` before execution. A Web gap can use `hexstrike-web-gap` only after
the index names the missing Strix capability.
