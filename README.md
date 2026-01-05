# StegBrain

Autonomous global state controller for the StegVerse-Labs cluster.

StegBrain does three things:

1. Reads machine-readable **status contracts** from cluster signal providers (starting with **StegDB**).
2. Produces a single cluster summary: `meta/global_status.json`.
3. Exposes a simple gating view (`ok` / `degraded` / `broken`) that other workflows can enforce (build-mode vs production-mode).

## Cluster state model

StegBrain reports one of:

- `ok` — required signals present and healthy
- `degraded` — required signals present but indicate partial impairment
- `broken` — a required signal is missing or indicates a hard failure

Missing required inputs are treated as `broken` with an explicit `reason` (e.g., `missing-signal`). “Unknown” is not a stable output state.

## Current signal providers

### StegVerse-Labs/StegDB
- `meta/dependency_status.json`  
  Must always be present. On failures it should still exist and report `state: degraded|broken` with a reason.
- `meta/aggregated_files.jsonl` (counts only)
