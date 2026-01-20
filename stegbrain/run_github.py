import json
import os
from pathlib import Path
from jsonschema import validate, ValidationError


def load_json(p: Path):
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_examples(repo_root: Path, core_schemas_dir: Path):
    results = []
    for p in sorted(repo_root.rglob("*.json")):
        if ".github" in p.parts:
            continue
        # validate only demo/example/meta JSON to avoid random JSON blobs
        if not any(x in p.parts for x in ("examples", "demo", "meta")):
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
        results = ["ℹ️ No eligible JSON found (validates only under examples/demo/meta)."]
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
