# Getting started

Run all commands from the repository root. The local validation step does not
need model credentials or a running tool container.

## 1. Check prerequisites

| Component | Needed for |
| --- | --- |
| Git, Python 3.10+, and a C compiler (`cc`) | Local validation and fixtures |
| Docker Compose 2.24.4+ | Configuration checks and the offline override |
| Docker Engine with BuildKit | Building and running the Linux tool image |
| OpenCode with a configured model | Interactive orchestration |
| Strix with a configured model | Web and application assessment lanes |
| Gitleaks 8.30.1 or a compatible version | Publication secret scan |

OpenCode and Strix are separate host applications. This repository includes
configuration and skills; it does not install those applications or configure
their model credentials. Use the official [OpenCode setup](https://opencode.ai/docs/)
and [Strix documentation](https://docs.strix.ai/). Keep provider keys outside Git
and the tool workbench.

The offline override uses Compose's `!override` and `!reset` tags. The minimum
version comes from the [Compose merge documentation](https://docs.docker.com/reference/compose-file/merge/).

```sh
python3 --version
docker compose version
./scripts/validate-release.sh
```

Expected: manifest, adapter, fixture, Compose policy, and local link checks
pass. Without Gitleaks, the script reports that the secret scan was not run.
Use `--require-secrets` before publication to make a missing scanner an error.
Compiler warnings from the deliberately vulnerable PWN fixtures are expected.

## 2. Prepare written scope

Copy the public template to a new private directory. Choose a distinct name
for each engagement; do not reuse the example directory for real work.

```sh
cp -R engagements/example engagements/my-lab
```

Edit these files before a run:

- `SCOPE.md`: authorization reference, exact assets, accounts, dates, allowed
  actions, prohibited actions, and stop conditions.
- `scope.json`: the same approved limits for the CTF adapter. Set an active
  UTC time window, one category, and only the approved targets or OSINT sources.
  Keep both KOTH effect flags false unless separately authorized.
- `INDEX.md`: the lane, owner, expected output, and later the evidence records.
- `strix-instructions.md`: instructions for a Strix lane, when needed.

The JSON template has an expired time window and empty category and target
lists. It is deliberately unusable until edited. The adapter implements
selected checks from the [scope contract](../contracts/scope.schema.json);
it does not run a full JSON Schema validator or validate the written approval.

Copy only approved artifacts and the completed JSON file into the input
workbench. The container sees this directory as read-only.

```sh
cp engagements/my-lab/scope.json workbench/input/scope.json
cp /absolute/path/to/approved-artifact workbench/input/challenge
```

## 3. Build the tool image

For a CTF lane, reserve at least 40 GiB of free space and build the native
image. The build downloads a large set of packages and source toolchains.

```sh
docker compose -f compose.hexstrike.yml build
```

The Dockerfile selects native AMD64 or ARM64 downloads and build steps. A
successful image build records the package and executable inventory under
`/opt/ctf-adapter/`; it does not prove each tool operation.

## 4. Start one service configuration

For artifact work that does not need a network, use the offline configuration:

```sh
docker compose \
  -f compose.hexstrike.yml \
  -f compose.hexstrike.offline.yml \
  up -d --wait
```

This uses an internal Docker network and clears the published HTTP port. MCP
still works through Docker exec. Use it for the full lifetime of the lane.

For an explicitly authorized network lane, use the base configuration:

```sh
docker compose -f compose.hexstrike.yml up -d --wait
```

The base configuration allows outbound bridge traffic and publishes the
upstream HTTP API at `127.0.0.1:8888`. That API is separate from the scoped CTF
adapter. Do not expose it on a public interface or treat it as scope-enforced.

Check the inventory already recorded at build time:

```sh
docker compose -f compose.hexstrike.yml exec -T hexstrike \
  cat /opt/ctf-adapter/tool-smoke.txt
```

Each line should identify a resolved executable, with no `MISSING` entries.
Do not run `ctf_adapter.capture_versions` in the running service: it writes
build records into `/opt/ctf-adapter`, which is read-only at runtime.

## 5. Select and close a lane

1. State **Mode 1** and record the approved lane in the private `INDEX.md`.
2. Open OpenCode from the repository root. Load `ctf-router`,
   `ctf-scope-and-evidence`, and the selected category skill.
3. Set only the matching `mcp.hexstrike_<category>.enabled` value to `true`
   in `opencode.json`. Reload the OpenCode session after a config change.
4. Keep the existing `ask` permissions. Approve each proposed tool call only
   when its target and effect match the written scope.
5. Inspect the tool's `result.json`, stdout, stderr, and artifacts under
   `workbench/output/evidence/`. Record the evidence under its original owner.
6. Set the MCP entry back to `false` and stop the service when the lane ends.

For example, the Reverse lane uses `hexstrike_reverse` and
`mcp-servers.hexstrike.reverse.json`. The latter is an alternative MCP client
configuration; OpenCode uses the entry in `opencode.json`.

The local permission rules use an initial broad deny rule followed by
profile-specific `ask` rules. OpenCode uses the last matching rule. See its
[permission documentation](https://opencode.ai/docs/permissions/).

For an offline lane, stop with the same file pair:

```sh
docker compose \
  -f compose.hexstrike.yml \
  -f compose.hexstrike.offline.yml \
  down
```

For a base configuration lane, use `docker compose -f compose.hexstrike.yml down`.
Stopping the service preserves workbench files. Restore all MCP entries to
disabled before committing project configuration.

## Web and application lanes

Strix owns these lanes. In Mode 1, run it without a HexStrike MCP connection.
Use a disposable clean checkout for source assessment and the completed
private instruction file. Model calls can incur provider charges.

After written scope and the spend limit are approved, a CLI invocation has
this form:

```sh
strix -n \
  --target /absolute/path/to/authorized-clean-checkout \
  --instruction-file ./engagements/my-lab/strix-instructions.md \
  --max-budget 10
```

Keep the Strix output and its validation state separate from adapter evidence.
A recorded Web capability gap must be approved and documented before opening
a separate `web-gap` lane.

## KOTH effects

King of the Hill (KOTH) operations use two independent sequences:

| Effect | Prepare | Execute after human approval |
| --- | --- | --- |
| Service patch | `koth_prepare_patch` | `koth_apply_patch` |
| Flag submission | `koth_prepare_flag_submission` | `koth_submit_flag` |

Inspect and approve the exact digest, target, and effect immediately before
execution. A digest is a content binding, not proof of human consent. The
adapter consumes it before the effect, so a failed or ambiguous result still
requires investigation before a new attempt. Patch approval does not authorize
flag submission. Keep rollback output and failed-run evidence.
