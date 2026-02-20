#!/usr/bin/env python3
"""
Validate graph-data.json against the JSON Schema and enforce logical invariants.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_schema(data: Any, schema: Any) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda err: err.path)
    return [f"Schema error at {'/'.join(map(str, err.path)) or '<root>'}: {err.message}" for err in errors]


def validate_invariants(data: dict) -> list[str]:
    errors: list[str] = []

    metadata = data.get("metadata", {})
    nodes = data.get("nodes", [])
    links = data.get("links", [])

    # Basic presence checks to avoid KeyError churn.
    if not isinstance(metadata, dict) or not isinstance(nodes, list) or not isinstance(links, list):
        return ["metadata, nodes, and links must be present and correctly typed"]

    node_ids = [node.get("id") for node in nodes]
    node_events = [node.get("events") for node in nodes]
    link_weights = [link.get("weight") for link in links]

    # All counts must be positive.
    for key in ("total_events", "total_agents", "total_collaborations", "unique_pairs", "day"):
        value = metadata.get(key)
        if not isinstance(value, int) or value <= 0:
            errors.append(f"metadata.{key} must be a positive integer (found {value!r})")

    for idx, events in enumerate(node_events):
        if not isinstance(events, int) or events <= 0:
            errors.append(f"nodes[{idx}].events must be a positive integer (found {events!r})")

    for idx, weight in enumerate(link_weights):
        if not isinstance(weight, int) or weight <= 0:
            errors.append(f"links[{idx}].weight must be a positive integer (found {weight!r})")

    # Unique node IDs.
    counts = Counter(node_ids)
    duplicates = [node_id for node_id, count in counts.items() if count > 1]
    if duplicates:
        errors.append(f"Duplicate node ids found: {', '.join(duplicates)}")

    node_id_set = set(node_ids)

    # Links must reference existing node IDs.
    for idx, link in enumerate(links):
        source = link.get("source")
        target = link.get("target")
        if source not in node_id_set:
            errors.append(f"links[{idx}].source references unknown node id '{source}'")
        if target not in node_id_set:
            errors.append(f"links[{idx}].target references unknown node id '{target}'")

    # Summation and count invariants.
    total_events_value = metadata.get("total_events")
    total_events_sum = sum(events for events in node_events if isinstance(events, int))
    if isinstance(total_events_value, int):
        if total_events_sum < total_events_value:
            errors.append(
                f"metadata.total_events ({total_events_value}) exceeds sum of node events ({total_events_sum})"
            )
        for idx, events in enumerate(node_events):
            if isinstance(events, int) and events > total_events_value:
                errors.append(
                    f"nodes[{idx}].events ({events}) exceeds metadata.total_events ({total_events_value})"
                )

    if metadata.get("total_agents") != len(nodes):
        errors.append(
            f"metadata.total_agents ({metadata.get('total_agents')}) does not match number of nodes ({len(nodes)})"
        )

    total_collaborations_expected = sum(weight for weight in link_weights if isinstance(weight, int))
    if metadata.get("total_collaborations") != total_collaborations_expected:
        errors.append(
            f"metadata.total_collaborations ({metadata.get('total_collaborations')}) does not match sum of link weights ({total_collaborations_expected})"
        )

    unique_pairs = {
        tuple(sorted((link.get("source"), link.get("target"))))
        for link in links
        if isinstance(link, dict)
    }
    if metadata.get("unique_pairs") != len(unique_pairs):
        errors.append(
            f"metadata.unique_pairs ({metadata.get('unique_pairs')}) does not match number of unique unordered pairs ({len(unique_pairs)})"
        )

    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    data_path = repo_root / "graph-data.json"
    schema_path = repo_root / "schema" / "graph-data.schema.json"

    if not data_path.exists():
        print(f"Missing data file: {data_path}", file=sys.stderr)
        return 1
    if not schema_path.exists():
        print(f"Missing schema file: {schema_path}", file=sys.stderr)
        return 1

    data = load_json(data_path)
    schema = load_json(schema_path)

    errors = validate_schema(data, schema)
    errors.extend(validate_invariants(data))

    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("graph-data.json is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
