#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
NOW = datetime.now(timezone.utc).isoformat()


def load_json(path: Path):
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_error": f"failed_to_parse:{type(e).__name__}", "_details": str(e)}


def determine_cluster_state(dep_status: dict | None):
    if dep_status is None:
        return "unknown", [], ["dependency_status.json missing from StegDB"]

    issues = dep_status.get("issues") or []
    global_ok = dep_status.get("global_ok", False)

    affected = sorted({i.get("repo", "_unknown") for i in issues if i.get("severity") in ("warning", "error")})

    if global_ok and not issues:
        return "ok", affected, []

    # Distinguish degraded vs broken later if we want; for now:
    if any(i.get("severity") == "error" for i in issues):
        return "degraded", affected, [i.get("message") for i in issues]
    else:
        return "degraded", affected, [i.get("message") for i in issues]


def evaluate_prod_gate(cluster_state: str, dep_status: dict | None, policy: dict):
    allow_unknown = bool(policy.get("allow_prod_if_unknown", False))
    required_repos = policy.get("required_repos_for_prod", [])
    min_agg = int(policy.get("min_aggregated_records", 1))

    if dep_status is None:
        if allow_unknown:
            return True, "No dependency_status.json yet; policy allows prod in unknown state."
        return False, "StegDB dependency_status.json missing; prod blocked."

    aggregated_records = dep_status.get("aggregated_records", 0)
    repos = dep_status.get("repos") or {}

    if cluster_state != "ok":
        return False, f"Cluster state is {cluster_state}; prod blocked."

    if aggregated_records < min_agg:
        return False, f"Only {aggregated_records} aggregated records; minimum {min_agg} required."

    for name in required_repos:
        rs = repos.get(name)
        if not rs:
            return False, f"Required repo {name} missing from dependency map."
        if rs.get("status") != "ok":
            return False, f"Required repo {name} status is {rs.get('status')}; prod blocked."

    return True, "All required repos healthy; prod allowed."


def main():
    stegdb_root = ROOT / "external" / "StegDB"
    dep_status_path = stegdb_root / "meta" / "dependency_status.json"
    dep_status = load_json(dep_status_path)

    policy = load_json(ROOT / "meta" / "brain_policy.json") or {}

    cluster_state, affected_repos, issue_messages = determine_cluster_state(dep_status)
    prod_allowed, prod_reason = evaluate_prod_gate(cluster_state, dep_status, policy)

    brain_output = {
        "generated_at": NOW,
        "sources": {
            "StegDB": {
                "dependency_status_present": dep_status is not None,
                "dependency_status_path": str(dep_status_path),
            }
        },
        "cluster": {
            "state": cluster_state,  # ok | degraded | broken | unknown
            "affected_repos": affected_repos,
            "issues": issue_messages,
        },
        "prod_gate": {
            "allowed": prod_allowed,
            "reason": prod_reason,
        }
    }

    out_path = ROOT / "meta" / "global_status.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(brain_output, indent=2), encoding="utf-8")

    print(f"[StegBrain] Updated global status: {out_path}")
    print(f"  cluster_state={cluster_state}")
    print(f"  prod_allowed={prod_allowed} ({prod_reason})")


if __name__ == "__main__":
    main()
