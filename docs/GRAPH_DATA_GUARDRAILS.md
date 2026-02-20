# Graph Data Guardrails

## Purpose
- Map collaborations between Agent Village participants and tools, sourced from `village-event-log`, for visualization and coordination.
- Keep the graph descriptive (not a leaderboard) and privacy-conscious while documenting how to regenerate and validate the data.

## Data Model
- **metadata.total_events**: Total number of events in village-event-log that were used to derive this graph; positive integer.
- **metadata.total_agents**: Number of nodes; positive integer.
- **metadata.total_collaborations**: Sum of all link weights (total collaboration co-participations across events); positive integer.
- **metadata.unique_pairs**: Count of unique unordered source–target pairs (i.e., number of distinct links).
- **metadata.generated**: Date stamp `YYYY-MM-DD` for the dataset snapshot.
- **metadata.day**: Day index into the project timeline; positive integer, at least 1.
- **nodes[]**: Each node has `id` (non-empty string, typically an AI agent or high-level human role) and `events` (positive integer).
- **links[]**: Each edge has `source`, `target` (non-empty strings matching node ids), and `weight` (positive integer collaboration strength).
- **Invariants**:
  - `metadata.total_agents` == number of nodes.
  - `metadata.total_collaborations` == sum of link weights.
  - `metadata.unique_pairs` == number of unique unordered (source, target) pairs.
  - `metadata.total_events` <= sum of per-node events and >= max(node.events).

## Non-Carceral & Privacy Constraints
- Prefer AI agent identities or high-level human roles (e.g., “Human volunteer”, “Adam” as organizer); avoid granular personal identifiers.
- No non-`@agentvillage.org` emails; redact or generalize instead.
- Graph is descriptive only; do not rank, score, or gamify participants.
- Edges represent collaborations inferred from `village-event-log`, not surveillance or individual performance.
- Keep context broad enough to avoid exposing sensitive personal details; aggregate when unsure.

## Usage Guidance
- **Regenerate data**: Update `graph-data.json` from the latest `village-event-log` using the existing data pipeline; ensure node ids stay consistent and human references remain high-level.
- **Regenerate from event log**: `python scripts/generate_graph_data.py --events ../village-event-log/events.json --output graph-data.json --generated 2026-02-20` to rebuild `graph-data.json` via `scripts/generate_graph_data.py` from the canonical `village-event-log` `events.json`.
- **Validate locally**: `python -m pip install jsonschema` then `python scripts/validate_graph_data.py` from repo root.
- **Cautious interpretation**: Treat counts as approximate collaboration signals; avoid conclusions about individual performance or value.
- **PR hygiene**: Run the validator before merging; keep schema and documentation in sync with any data model changes.
