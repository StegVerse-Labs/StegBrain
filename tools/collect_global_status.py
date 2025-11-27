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

def count_jsonl_lines(path: Path) -> int:
    if not path.is_file():
        return 0
    return sum(1 for _ in path.open("r", encoding="utf-8"))

def determine_cluster_state(dep_status):
    """
    Converts StegDB dependency status into cluster brain state.
    """
    if dep_status is None:
        return "unknown", [{"source": "StegDB", "issue": "missing_dependency_status"}]

    if isinstance(dep_status, dict):
        global_ok = dep_status.get("global_ok")
        issues = dep_status.get("issues") or []

        if global_ok is True:
            return "ok", issues
        if global_ok is False:
            return "degraded", issues

    return "unknown", [{"source": "StegDB", "issue": "malformed_dependency_status"}]

def main():
    stegdb_root = ROOT / "external" / "StegDB"

    dep_status_path = stegdb_root / "meta" / "dependency_status.json"
    aggregated_files_path = stegdb_root / "meta" / "aggregated_files.jsonl"

    dep_status = load_json(dep_status_path)
    aggregated_count = count_jsonl_lines(aggregated_files_path)

    cluster_state, issues = determine_cluster_state(dep_status)

    brain_output = {
        "generated_at": NOW,
        "sources": {
            "StegDB": {
                "dependency_status_present": dep_status is not None,
                "aggregated_files_count": aggregated_count,
            }
        },
        "cluster": {
            "state": cluster_state,   # ok | degraded | broken | unknown
            "issues": issues,
        }
    }

    out_path = ROOT / "meta" / "global_status.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(brain_output, indent=2), encoding="utf-8")

    print(f"[StegBrain] Updated global status: {out_path}")

if __name__ == "__main__":
    main()
