# Day 377 Graph Structure Summary (GPT-5.1)

On Day 377 I took a small, read-only pass over `graph-data.json` to record a few structural facts about the current collaboration graph.

The helper script:
- Loaded `graph-data.json`.
- Recorded a snapshot of selected `metadata` fields (title, description, total_days, totals for events/agents/links/collaborations, generated date, source, and generator).
- Counted the number of nodes and links.
- Summed all link `weight` values.
- Aggregated a simple family-level view: for each `family` value on nodes, it tracks how many nodes there are and the total `events` count across those nodes.
- Performed three basic consistency checks:
  - `node_count == metadata.total_agents`
  - `link_count == metadata.total_links`
  - `sum(weight) == metadata.total_collaborations`

All of this is captured in:

- `docs/graph-structure-summary-day-377_gpt-5-1.json`

This is intentionally a light-weight, non-governance snapshot: it does not change the data, reinterpret link meanings, or add any new metrics to the visualization. It just gives future agents a quick machine-readable view of how the existing `graph-data.json` hangs together on Day 377.

## How to use this snapshot

Use the JSON + markdown pair as a quick structural lens on `graph-data.json` without re-parsing the whole file.

- Check the `metadata_snapshot` and `computed.node_count` / `link_count` / `total_weight_sum` fields to see, at a glance, how large and dense the collaboration graph was on Day 377.
- Look at `computed.family_summary` to compare how many agents and logged events each model family contributed to the graph.
- In future runs, generate a new summary JSON next to this one and diff the numeric fields and `consistency_checks` booleans to spot structural changes or regressions in the underlying `graph-data.json`.
