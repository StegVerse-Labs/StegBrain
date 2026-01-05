#!/usr/bin/env python3
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def main() -> int:
    """
    Reads a local file (downloaded from StegDB) at:
      meta_sources/stegdb_dependency_status.json

    Writes:
      meta/global_status.json

    Fail-closed behavior:
      - If missing/unreadable -> global state = broken
      - No 'unknown' allowed
    """
    src = Path("meta_sources/stegdb_dependency_status.json")
    out = Path("meta/global_status.json")
    out.parent.mkdir(parents=True, exist_ok=True)

    # Default: fail-closed
    global_state = "broken"
    reason = "missing-stegdb-dependency-status"
    details = {
        "source": "StegBrain",
        "generated_at_utc": utc_now(),
        "inputs": {}
    }

    if src.exists():
        payload = load_json(src)
        if isinstance(payload, dict):
            state = payload.get("state")
            provider = payload.get("provider", "StegDB")
            why = payload.get("reason", "no-reason")

            details["inputs"][provider] = payload

            if state in ("ok", "degraded", "broken"):
                # Map directly (you can later add multi-source logic)
                global_state = state
                reason = f"stegdb:{why}"
            else:
                global_state = "broken"
                reason = "invalid-stegdb-state"
        else:
            global_state = "broken"
            reason = "unreadable-stegdb-json"

    global_payload = {
        "provider": "StegBrain",
        "state": global_state,
        "reason": reason,
        "generated_at_utc": utc_now(),
        "details": details,
    }

    out.write_text(json.dumps(global_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(global_payload))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
