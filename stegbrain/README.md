# StegBrain Ops Agent

This module implements the **StegBrain Ops Agent** — a repo-local,
read-only automation persona used for:

- intake validation
- schema compliance checking
- ops hygiene and reporting

## Relationship to StegBrain Core

StegBrain has two layers:

1. **StegBrain Core (root-level)**
   - Global cluster state controller
   - Produces `meta/global_status.json`
   - Gates build vs production workflows

2. **StegBrain Ops Agent (this module)**
   - Repo-scoped assistant
   - Validates inputs against DiamondOps-Core schemas
   - Produces comments and summaries
   - Never makes global decisions

The Ops Agent does **not** modify cluster state.
It exists to improve signal quality *before* signals reach StegBrain Core.

## Safety & Scope

The Ops Agent:
- does not control equipment
- does not bypass safety systems
- does not require secrets
- does not block merges by default

It assists humans and upstream systems by improving data quality.
