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
    count = 0
    with path.open("r", encoding="utf-8") as f:
        for _ in f:
            count += 1
    return count

def main():
    # Where StegDB will be checked out by the workflow
    stegdb_root = ROOT / "external" / "StegDB"

    dep_status_path = stegdb_root / "meta" / "dependency_status.json"
    aggregated_files_path = stegdb_root / "meta" / "aggregated_files.jsonl"

    dep_status = load_json(dep_status_path)
    aggregated_count = count_jsonl_lines(aggregated_files_path)

    # Determine overall health from dependency_status.json if present
    global_ok = None
    issues = []

    if isinstance(dep_status, dict):
        global_ok = dep_status.get("global_ok")
        if not isinstance(global_ok, bool):
            global_ok = None

        detected_issues = dep_status.get("issues") or []
        if isinstance(detected_issues, list):
            for issue in detected_issues:
                if isinstance(issue, dict):
                    issues.append(issue)
                else:
                    issues.append({"raw": issue})
    elif dep_status is None:
        issues.append({"source": "StegDB", "reason": "missing_dependency_status"})
    else:
        issues.append({"source": "StegDB", "reason": "invalid_dependency_status_format"})

    # Fallback if we couldn't determine global_ok
    if global_ok is None:
        global_state = "unknown"
    elif global_ok:
        global_state = "ok"
    else:
        global_state = "degraded"

    output = {
        "generated_at": NOW,
        "sources": {
            "StegDB": {
                "dependency_status_present": dep_status is not None,
                "aggregated_files_count": aggregated_count,
            }
        },
        "global": {
            "state": global_state,  # "ok" | "degraded" | "unknown"
            "ok": bool(global_ok) if isinstance(global_ok, bool) else None,
        },
        "issues": issues,
    }

    meta_dir = ROOT / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    out_path = meta_dir / "global_status.json"
    out_path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Wrote global status to {out_path}")

if __name__ == "__main__":
    main()
