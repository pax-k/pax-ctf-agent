# Troubleshooting

Run the diagnostic first:

```sh
./scripts/doctor
```

## Native backend does not start

Run `./scripts/setup` again. It reports missing Git or Python and restores the
pinned HexStrike checkout and virtual environment. Check that port 8888 is not
used by another local service.

## OpenCode cannot connect to HexStrike

Start the native backend with `./scripts/start-hexstrike`, then run
`./scripts/doctor`. OpenCode starts the MCP bridge from `scripts/hexstrike-mcp`.
It needs the native service to be healthy on localhost.

## Strix needs HexStrike tools

Use `./scripts/run-strix -- <Strix arguments>`. The wrapper supplies the
restricted MCP configuration. Do not add the unrestricted OpenCode MCP server
to a Strix run.

## Blockchain tools are unavailable

Blockchain tools are part of the optional Docker lab. Run `./scripts/setup
--lab`, then `./scripts/start-hexstrike --lab`. Enable `hexstrike_lab` in
OpenCode after the backend starts.

## Both backends appear active

Only one backend can own port 8888. Stop the backend you started before
starting the other. `./scripts/doctor` reports the tracked native process and
the lab Compose service.
