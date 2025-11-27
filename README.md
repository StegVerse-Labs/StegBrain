# StegBrain

Autonomous global state controller for the StegVerse-Labs cluster.

StegBrain:

- Aggregates signals from all guardian repos (starting with StegDB)
- Produces `meta/global_status.json`
- Exposes a canonical cluster state: `ok`, `degraded`, `broken`, `unknown`
- Maintains build-mode vs production-mode cluster enforcement
- Enables "cannot deploy if cluster brain says no"

This is the StegVerse control brain.

# StegBrain

Global health and dependency brain for the StegVerse-Labs cluster.

StegBrain does **three main things**:

1. Reads dependency + metadata signals from guardian repos (starting with **StegDB**).
2. Produces a single `meta/global_status.json` summary for the whole cluster.
3. Exposes a simple “OK / DEGRADED / BROKEN” view that other workflows can gate on.

Current data sources:

- `StegVerse-Labs/StegDB`
  - `meta/dependency_status.json`
  - `meta/aggregated_files.jsonl` (for counts only)
