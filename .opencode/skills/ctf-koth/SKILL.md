---
name: ctf-koth
description: Diagnose and prepare repairs for an authorized KOTH service while requiring separate human approval for each patch application and flag submission.
license: Apache-2.0
---

# Operate a KOTH lane

Use `hexstrike-koth` only when `scope.json` enables the exact KOTH effects.
Snapshot the supplied service into the writable workbench, diagnose it, and
prepare a patch. Validate the patch and its regression tests before requesting
approval.

`koth_prepare_patch` returns a digest for the exact patch and target checkout.
Ask the human to approve that digest immediately before `koth_apply_patch`.
Approval does not carry to another patch.

Prepare flag submission separately. Ask the human to approve the flag digest,
team, target, and endpoint immediately before `koth_submit_flag`. Never infer
approval from the challenge request, a prior patch, or a prior flag. Stop after
one failed or ambiguous mutation and preserve the evidence and rollback file.
