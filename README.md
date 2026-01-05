# StegBrain

Autonomous global state controller for the StegVerse-Labs cluster.

StegBrain does three things:

1. Reads machine-readable **status contracts** from cluster signal providers (starting with **StegDB**).
2. Produces a single cluster summary: `meta/global_status.json`.
3. Exposes a simple gating view (`ok` / `degraded` / `broken`) that other workflows can enforce (build-mode vs production-mode).

StegBrain is the StegVerse control brain: it turns many repo-level signals into one cluster decision.

---

## Cluster state model

StegBrain reports one of:

- `ok` — required signals present and healthy
- `degraded` — required signals present but indicate partial impairment
- `broken` — a required signal is missing or indicates a hard failure

**Missing required inputs are treated as `broken` with an explicit `reason`** (e.g., `missing-signal`).  
“Unknown” is not a stable output state. It may appear as a transient observation internally, but StegBrain output must be actionable.

---

## Outputs

### `meta/global_status.json`

A single, canonical cluster view intended for gating deploys and automation decisions.

Typical fields include:

- `state`: `ok | degraded | broken`
- `reasons`: list of machine-readable reason strings
- `sources`: per-provider snapshot of state + reason
- `generated_at_utc`: timestamp

(See `schemas/global_status.schema.json` if present.)

---

## Build-mode vs production-mode

StegBrain supports the pattern:

- Build-mode: allow progress while surfacing degradation.
- Production-mode: block deployment if cluster state is not `ok`.

Downstream repos should gate production deploys on StegBrain state.

---

## Current signal providers

### StegVerse-Labs/StegDB

StegBrain currently consumes:

- `meta/dependency_status.json`  
  **Must always be present.** If StegDB cannot complete its cycle, it should still write this file with `state: degraded|broken` and an explicit reason.
- `meta/aggregated_files.jsonl` (counts only; informational)

---

## Design principles

- **Contract-driven:** providers emit explicit status; StegBrain never guesses.
- **Fail-closed for prod:** missing required signals → `broken`.
- **Human-auditable:** reasons are explicit and traceable to sources.
- **Composable:** adding new providers (e.g., StegValue later) should not require changing core semantics.
