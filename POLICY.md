# StegBrain Policy

## Default behavior (warn-only)
StegBrain is advisory by default:
- validates inputs and contracts
- posts summaries / guidance
- does not block merges by default
- does not make operational decisions

## Enforcement changes
Any move to enforcement (required checks, blocking PRs, production gating) must be:
- explicitly approved
- documented in the affected repo
- rolled out intentionally (warn → soft fail → gate), if ever

## Safety posture
StegBrain does not provide bypass guidance and does not require secrets by default.
