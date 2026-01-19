import json
import os
from pathlib import Path
from jsonschema import validate, ValidationError

CORE_SCHEMA_DIR = Path("../DiamondOps-Core/schemas")

def load_schema(schema_name):
    schema_path = CORE_SCHEMA_DIR / schema_name
    if not schema_path.exists():
        return None
    with open(schema_path) as f:
        return json.load(f)

def validate_json(file_path):
    with open(file_path) as f:
        data = json.load(f)

    schema_name = file_path.name.replace(".json", ".schema.json")
    schema = load_schema(schema_name)

    if not schema:
        return f"⚠️ No matching schema found for `{file_path.name}`"

    try:
        validate(instance=data, schema=schema)
        return f"✅ `{file_path.name}` valid against `{schema_name}`"
    except ValidationError as e:
        return f"❌ `{file_path.name}` failed validation: {e.message}"

def scan_repo():
    results = []
    for path in Path(".").rglob("*.json"):
        if ".github" in path.parts:
            continue
        results.append(validate_json(path))
    return results

def main():
    print("StegBrain running...")
    results = scan_repo()
    print("\n".join(results))

if __name__ == "__main__":
    main()
