# Security Policy

## Supported version

This project does not have a stable release yet. Report issues against the
latest commit on the default branch.

## Report a vulnerability

Do not open a public issue for a vulnerability that can expose credentials,
assessment evidence, target details, or a practical exploitation path.

Use GitHub private vulnerability reporting when it is enabled for this
repository. If it is not enabled, contact the repository owner through a
private channel listed on the owner's GitHub profile. Include the affected
revision, impact, reproduction conditions, and a minimal non-destructive proof.
Do not include real secrets or third-party data.

## Safe research boundary

Test this project only in a disposable lab or on assets for which you have
explicit written authorization. Do not test repository maintainers, users,
dependencies, or service providers as part of a report.

The MCP allowlists restrict tool names. They do not validate network scope,
target identity, authorization, or impact. Container isolation also does not
grant authority to test a target.

## Sensitive assessment data

Engagement scopes, credentials, logs, reports, findings, and evidence are not
public project files. Keep them in ignored engagement directories or another
approved private evidence store. Revoke and rotate any credential that enters
Git history or a public issue.
