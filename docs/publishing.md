# Publish the source to GitHub

Publish this project as an experimental source repository only after the
checks below pass and the owner approves the destination and visibility.
Publishing the source does not establish a supported release or authorize a
security assessment.

## Current release boundary

- The root project license is Apache-2.0.
- The source includes vendored skills with separate licenses. The missing
  upstream notice for twelve mobile/CI/CD skills remains an open item in
  [third-party notices](../THIRD_PARTY_NOTICES.md).
- Full AMD64/ARM64 image builds and MCP tool execution require separate proof.
  Local checks alone are sufficient to describe tested source behavior, not
  to claim that the full workstation is validated.
- Container image publication requires a separate review of resolved packages
  and license obligations. The CI workflow does not upload images.

## 1. Review the public file set

```sh
git status --short
git ls-files --cached --others --exclude-standard
git ls-files --cached --ignored --exclude-standard
```

The last command must return no files. Ignore rules do not remove files that
were already staged or committed.

Only the sanitized `engagements/example/` files and workbench `.gitkeep`
markers belong in the public set. Keep private scopes, target identities,
credentials, logs, findings, and evidence out of commits. Review third-party
skill examples as well as project files. A secret scanner cannot identify all
private information.

## 2. Run the publication checks

Install [Gitleaks](https://github.com/gitleaks/gitleaks#installing) and run:

```sh
./scripts/validate-release.sh --require-secrets
```

The script validates public JSON, shell syntax, manifests, skill hashes,
generated coverage, adapter tests, local fixtures, Compose policies, Markdown
links, and ignore boundaries. It scans a temporary copy of the Git candidate
files with Gitleaks and redacts secret values from scanner output.

This directory scan covers current file content. For a repository with existing
commits, also scan history before publication:

```sh
gitleaks git . --no-banner --redact
```

Review any finding before changing an allowlist. Do not bypass a detected
credential with a broad exclusion.

## 3. Review the release candidate

Resolve the skill license notice item. Confirm that all MCP entries are
disabled and the example scope remains inactive. Review the exact staged
content before the first commit:

```sh
git diff --cached --stat
git diff --cached --check
git diff --cached
```

Choose the repository owner, name, and visibility explicitly. Do not use an
existing remote without checking that it is the approved destination. Commit,
create the remote repository, and push only after those actions are authorized.

## 4. Verify GitHub after the push

Confirm the published file list and default branch. Enable GitHub private
vulnerability reporting, or provide a working private contact in
[SECURITY.md](../SECURITY.md).

The first push to `main` triggers local validation, a secret scan, and two
native image builds. Those builds can run for hours. Inspect their actual
results before claiming architecture support. Review the uploaded SPDX and
Trivy reports; vulnerability findings currently do not fail the workflow.

Use a branch rule to require the checks appropriate to the release. Keep
private assessments, flags, and provider credentials out of issues, pull
requests, workflow logs, and release assets.
