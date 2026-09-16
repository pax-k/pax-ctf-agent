# Example Assessment Scope

Copy this directory to a new, ignored engagement directory. Replace every
placeholder before testing. Do not commit the completed scope, credentials,
target details, findings, or evidence.

The matching JSON template has an expired time window, no allowed categories
or targets, and both KOTH effects disabled. Set only the values covered by the
written authorization. Use `INDEX.md` to record lane ownership and evidence.

## Authorization

- Engagement owner: `<name and organization>`
- Written authorization reference: `<contract, ticket, or approval reference>`
- Start time: `<ISO 8601 timestamp and time zone>`
- End time: `<ISO 8601 timestamp and time zone>`
- Selected operating mode: `<Mode 1 or Mode 2>`

## Authorized assets

- Application or repository: `<exact authorized target>`
- Accounts and roles: `<test accounts only; do not put passwords or tokens here>`
- Source revision: `<commit SHA when applicable>`
- Network ranges: `<exact CIDR ranges, or none>`

## Allowed actions

- `<specific action>`
- `<specific action>`

## Prohibited actions

- Denial of service or destructive tests
- Persistence
- Real-secret exfiltration
- Access to third-party assets
- `<engagement-specific restriction>`

## Stop conditions

- Target identity or authorization becomes uncertain.
- The test can affect data, users, or assets outside the authorized scope.
- A prohibited action would be necessary to continue.
- `<engagement-specific stop condition>`

## Evidence and retention

- Evidence directory: `engagements/<id>/evidence/`
- Retention period: `<duration>`
- Approved recipients: `<people or team>`
- Required redaction: `<rules>`
