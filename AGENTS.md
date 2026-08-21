# Repository Agent Contract

## Mission

Own autonomous-vehicle operational evidence for this repository: permits, testing/deployment activity, miles/disengagements, incidents and other official observations represented by the project. Produce reproducible operational evidence, not market-size or valuation forecasts.

## Canonical authority

- Prefer DMV/NHTSA and other competent government/regulatory sources, plus official operator disclosures only for fields they directly own.
- Preserve operator/vehicle/program identity, jurisdiction, observation/report period, unit, source URL, retrieval time and revision/provenance fields required by the dataset.
- Keep official operational observations separate from ARK forecasts, enterprise value, scenario models and investment conclusions.
- Cross-repository forecast comparison belongs in `investor2`; do not copy ARK forecast facts here unless the repository itself owns a distinct source contract.

## Autonomous execution

1. Inspect current `main`, README, open Issues/PRs, canonical raw/derived data, workflows/tests and public outputs.
2. Continue one canonical workline before creating another collector, schema, branch or Issue.
3. Prefer newly verified operational records, identity/period corrections, deterministic comparisons, public usability, then simplification.
4. Require definition/unit/jurisdiction comparability before calculating cross-operator or cross-period differences.
5. Run focused deterministic checks and verify the exact reviewed revision before merge.
6. Stop at the fixed point; do not add valuation or adoption forecasts merely because operational data changed.

## Branch lifecycle

- Aside from the default branch and unavoidable platform-managed/protected branches, a persistent branch is permitted only while it is the head branch of a currently open PR.
- Creating a work branch creates an obligation to open or reuse its canonical PR immediately; do not use branches as backlog, continuation state, backup, archive, or evidence storage.
- After a PR is merged or closed, delete its head branch after verifying PR/main state. A branch with no open PR is an orphan and must be deleted.
- Before and after work, compare repository branches with open PR heads. Do not report cleanup/fixed point while an orphan task branch remains.
- If the available tool cannot delete a branch, record that as a tooling blocker and do not claim cleanup complete. Never create another orphan branch as a workaround.

## Merge and release are separate

### PR merge conditions

A PR may merge when the repository-local operational-data contract is correct on the exact head revision: source identity, jurisdiction, period and unit semantics are preserved, focused deterministic tests pass, generated artifacts are reproducible where affected, and no unresolved review or correctness blocker remains.

A future DMV/NHTSA release, post-merge live fetch, deployed public output, or real-world commercial operation is **not** a merge condition unless the PR specifically changes the release/live-acquisition mechanism and that mechanism must be validated before merge.

### Product/data release conditions

Release is a separate post-merge decision. Treat autonomous-vehicle evidence/views as released only after the merged `main` revision is read back and the release requirements in scope are actually executed, including fresh official source acquisition when required, published/generated artifacts, public surface if any, deployment identity, and rollback/rebuild path.

A merged PR does not prove commercial deployment, safety, or production release. A release/live-source blocker may block release without invalidating a correctly merged repository change. Report merge and release independently.

## Boundaries

- Testing miles, disengagements, permits and incidents are not interchangeable measures of commercial deployment or safety.
- Do not infer unreported miles, fleets, rides, revenue, market share or enterprise value.
- Do not execute trades or account actions.
- Unobserved source, CI, deployment or real-world operating outcomes remain unverified.

## Completion report

Report verified operational evidence Before -> After, primary source/canonical artifact, Issue/PR/commit/check evidence, then report `merged` and `released` separately with direct evidence for each. Include branch cleanup state, manual work removed and the remaining blocker.