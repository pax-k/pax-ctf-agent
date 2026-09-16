# Example evidence index

Copy this file with the scope template. Replace placeholders only in the
private engagement directory. Do not commit real assessment records here.

## Selected lane

- Operating mode: `<Mode 1 or Mode 2>`
- Lane and owner: `<category and responsible tool or skill>`
- Authorized asset: `<exact target or artifact>`
- Expected output: `<result and evidence needed>`
- State: `<planned, running, completed, failed, or stopped>`

## Evidence records

| Asset | Lane | Owner | Tool or skill | Timestamp (UTC) | Validation state | Evidence path | Original source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<asset>` | `<lane>` | `<owner>` | `<tool>` | `<timestamp>` | `<state>` | `<private path>` | `<run or source reference>` |

Keep evidence under its owner: `strix`, `opencode-mobile`, `opencode-cicd`,
`opencode-ctf`, `hexstrike`, or `koth`. Record a tool's completion separately
from finding validation. Failed, partial, timed-out, and skipped work remains
part of the record.

## Gaps and stop conditions

Record untested behavior, missing evidence, and the reason a lane stopped.
For a Web gap, record the specific missing Strix capability before enabling
the exceptional profile.
