# Authorized security work

Use this repository only on systems covered by written authorization.

OpenCode routes each surface to one planner:

- **Strix** owns web, API, application source, LLM application, AWS,
  Kubernetes, Active Directory, and dependency assessments. It can use the
  restricted HexStrike MCP tools as an executor.
- **OpenCode** owns reverse engineering, PWN, forensics, crypto, OSINT,
  blockchain, and miscellaneous artifact work. It loads the matching category
  skill and calls HexStrike directly.
- For mixed work, split the request by surface. Do not run Strix and OpenCode
  HexStrike tools against the same surface.

HexStrike executes selected operations. It does not plan an assessment or
write the assessment report. Do not use its AI planning, autonomous scanning,
generic command, package-installation, or unrestricted file tools.

Before active testing, confirm the authorized assets, accounts, time window,
and prohibited actions. Do not extract real secrets, retain credentials,
install persistence, delete evidence, deny service, or affect third parties.
Stop when target identity, scope, or impact is uncertain.

Private targets, evidence, logs, and engagement notes belong in ignored local
paths. Do not add them to Git.
