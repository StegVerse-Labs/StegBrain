import json
import os
from pathlib import Path
from jsonschema import validate, ValidationError


ALLOWLIST_FILENAME = "stegbrain.allowlist"


def load_json(p: Path):
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_allowlist(repo_root: Path):
    """
    Reads repo_root/stegbrain.allowlist if present.

    Format:
      - one path prefix per line
      - blank lines and lines starting with # are ignored
      - prefixes are treated as directory prefixes (e.g. 'examples/' or 'meta/')
    """
    allowlist_path = repo_root / ALLOWLIST_FILENAME
    if not allowlist_path.exists():
        return None  # means "no allowlist provided"

    prefixes = []
    for raw in allowlist_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # Normalize separators and ensure trailing slash for prefix matching.
        line = line.replace("\\", "/")
        if not line.endswith("/"):
            line = line + "/"
        prefixes.append(line)
    return prefixes or []  # empty list means "validate nothing eligible"


def _path_matches_prefixes(path: Path, repo_root: Path, prefixes):
    """
    Returns True if path (relative to repo_root) starts with any prefix.
    """
    rel = path.resolve().relative_to(repo_root.resolve()).as_posix()
    # Match both directory itself and files under it:
    # - prefix "meta/" should match "meta/foo.json"
    return any(rel.startswith(pref) for pref in prefixes)


def _default_eligible(path: Path):
    """
    Backwards-compatible behavior if no allowlist is present.
    Only validate JSON under examples/, demo/, or meta/.
    """
    return any(x in path.parts for x in ("examples", "demo", "meta"))


def validate_examples(repo_root: Path, core_schemas_dir: Path):
    prefixes = _read_allowlist(repo_root)

    results = []
    for p in sorted(repo_root.rglob("*.json")):
        if ".github" in p.parts:
            continue

        # If allowlist exists, use it. Otherwise use default eligibility rules.
        if prefixes is not None:
            if not _path_matches_prefixes(p, repo_root, prefixes):
                continue
        else:
            if not _default_eligible(p):
                continue

        schema_name = p.name.replace(".json", ".schema.json")
        schema_path = core_schemas_dir / schema_name
        if not schema_path.exists():
            results.append(f"⚠️ `{p.as_posix()}`: no matching schema `{schema_name}` in Core.")
            continue

        try:
            schema = load_json(schema_path)
            data = load_json(p)
            validate(instance=data, schema=schema)
            results.append(f"✅ `{p.as_posix()}` valid against `{schema_name}`")
        except ValidationError as e:
            results.append(f"❌ `{p.as_posix()}` failed validation: {e.message}")
        except Exception as e:
            results.append(f"❌ `{p.as_posix()}` error: {str(e)}")

    if not results:
        if prefixes is not None:
            results = [f"ℹ️ No eligible JSON found (allowlist `{ALLOWLIST_FILENAME}` matched nothing)."]
        else:
            results = ["ℹ️ No eligible JSON found (validates only under examples/demo/meta by default)."]

    return results


def main():
    repo_root = Path(os.environ.get("REPO_ROOT", ".")).resolve()
    core_dir = Path(os.environ.get("CORE_DIR", "./core")).resolve()
    core_schemas_dir = core_dir / "schemas"

    stegbrain_version = os.environ.get("STEGBRAIN_VERSION", "0.1.0")
    core_version = os.environ.get("CORE_VERSION", "v0.3.x")

    results = validate_examples(repo_root, core_schemas_dir)

    comment = "\n".join([
        "### 🧠 StegBrain Report",
        f"- StegBrain: `{stegbrain_version}`",
        f"- DiamondOps-Core: `{core_version}`",
        "",
        *results,
        "",
        "> Policy: advisory only (warn-only). No merges are blocked by StegBrain."
    ])

    out = {"comment": comment, "results": results}
    out_path = Path(os.environ.get("OUTPUT_PATH", "./stegbrain_output.json")).resolve()
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
