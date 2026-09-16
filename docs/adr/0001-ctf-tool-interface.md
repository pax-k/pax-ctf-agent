# ADR 0001: CTF Tool Interface

## Status

Accepted on 2026-09-16.

## Requirement

OpenCode needs category-specific CTF tools in the isolated HexStrike service.
Tool calls must have a small interface, validate paths and network scope, use
structured process arguments, save evidence, and keep upstream HexStrike at a
pinned revision.

## Designs considered

### Extend the upstream HexStrike server and MCP files

This reuses its HTTP client and tool registration. It also requires a large
patch to two monolithic upstream files. Several upstream wrappers construct
shell commands as strings. The patch would be difficult to review and would
conflict with upstream updates.

### Add one generic command tool

This has the smallest code surface, but it gives callers an arbitrary command
boundary. Profiles cannot express the intended operation, and argument or
scope policy becomes difficult to enforce.

### Run a local CTF adapter beside the pinned HexStrike server

The adapter uses the existing container, Python runtime, FastMCP transport, and
installed toolchain. It registers only named operations from a reviewed
registry. It validates paths, scope, options, timeouts, and output size before
calling a process with an argument array. Upstream HexStrike remains unchanged.

## Decision

Use the local CTF adapter. Each MCP configuration starts the adapter with one
profile. The profile determines which tools are registered, so the server does
not rely only on a client-side allowlist. The catalog profile exposes inventory
only. The original HexStrike API remains available for its existing supported
use, but it is not the CTF execution contract.

This design has a slightly larger local implementation than a generic command
tool. It gives a smaller authority surface, stable result schema, testable
validation, and a clear upstream boundary.

## Compatibility

`gdb_peda_debug` is removed. Its replacement is `gdb_pwndbg_debug`. Existing
binary and forensics profile users must select one of the new category
profiles.
