# Pax CTF Agent

Pax CTF Agent gives OpenCode one local routing model for authorized
security work. It uses Strix for application assessments and HexStrike for
specialist artifact work.

## Quick start

Install OpenCode, Strix, Git, and Python 3.10 or later. Then run:

```sh
./scripts/setup
./scripts/start-hexstrike
opencode
```

OpenCode loads `ctf-router` first, then the relevant skill. The `ctf-*` names
are stable skill identifiers. They describe categories and do not require a
competition workflow.

## Environment variables

Self-hosted Strix assessments need an LLM model and its provider API key:

| Variable | Required | Purpose |
| --- | --- | --- |
| `STRIX_LLM` | For self-hosted Strix | LiteLLM model identifier, for example `openai/gpt-5.4` |
| `LLM_API_KEY` | For self-hosted Strix | API key for the provider selected by `STRIX_LLM` |
| `HEXSTRIKE_PORT` | No | Local HexStrike port; defaults to `8888` |

Create a local file from the safe example and replace its dummy values:

```sh
cp .env.example .env
```

The project scripts do not load `.env` automatically. Export its values into
the current shell before you start OpenCode or run Strix:

```sh
set -a
. ./.env
set +a
```

Do not commit `.env` or real API keys. The managed Strix cloud workflow does
not use `STRIX_LLM` or `LLM_API_KEY`.

## Routing

| Work surface | Planner | HexStrike use |
| --- | --- | --- |
| Web, API, source, LLM application, AWS, Kubernetes, Active Directory, dependencies | Strix | Strix may use the restricted native MCP tools |
| Reverse engineering, PWN, forensics, crypto, OSINT, misc artifacts | OpenCode | Native HexStrike |
| Blockchain or a tool missing from native HexStrike | OpenCode | Optional lab backend |
| Mixed request | OpenCode splits surfaces | One planner per surface |

Do not call OpenCode HexStrike tools on a surface that Strix owns.

## Native and lab backends

The default backend is a pinned upstream HexStrike checkout in `.hexstrike/`.
It is small and provides the normal artifact path.

The optional lab backend preserves the existing full Docker toolchain,
including blockchain tools. It needs Docker Compose and about 40 GiB of free
disk space:

```sh
./scripts/setup --lab
./scripts/start-hexstrike --lab
```

Only one backend can run at a time. The optional `hexstrike_lab` MCP entry is
disabled by default. Enable it in OpenCode only after the lab backend starts.

## Safety

Use this project only with written authorization for the exact target and time
window. Native HexStrike is reachable only on localhost. Tool permissions do
not grant permission to test a target.

Read [the routing model](./docs/architecture.md) before an assessment. Use
[troubleshooting](./docs/troubleshooting.md) if setup or a backend fails.

Private evidence, targets, and credentials are ignored by Git. This repository
contains no engagement template and no sample targets.

## Development and publication

Run `./scripts/check.sh` before a pull request. It validates the shell and
configuration files without building the optional lab image.

The repository is prepared for source publication. Creating a GitHub
repository, choosing its visibility, and pushing remain separate actions.
