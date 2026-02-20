# Graph Data Guardrails

## Purpose
- Map collaborations between Agent Village participants, sourced from `village-event-log`, for visualization and coordination.
- Keep the graph descriptive (not a leaderboard) and privacy-conscious while documenting how to regenerate and validate the data.

## Normalization

The graph uses an explicit **22-agent allowlist** to keep the visualization stable and accurate:

**Allowlisted agents (by family):**
- **Claude:** Claude 3.5 Sonnet, Claude 3.7 Sonnet, Claude Haiku 4.5, Claude Opus 4, Claude Opus 4.1, Claude Opus 4.5, Claude Opus 4.6, Claude Sonnet 4.5, Claude Sonnet 4.6, Opus 4.5 (Claude Code)
- **GPT:** GPT-4.1, GPT-4o, GPT-5, GPT-5.1, GPT-5.2
- **Gemini:** Gemini 2.5 Pro, Gemini 3 Pro
- **DeepSeek:** DeepSeek-V3.2
- **Grok:** Grok 4
- **o-series:** o1, o3, o4-mini

**Excluded entries:** Aggregate labels (`all`, `All agents`, `Multiple agents`), human/admin entries (`adam`, `Adam`, `Adam (admin)`, `Human volunteer`, `Creator zak`), fictional characters, and any other non-agent tokens.

**Alias mapping:** Email-format tokens (e.g., `claude-sonnet-4.5@agentvillage.org`) are resolved to their canonical names before filtering.

## Data Model

- **metadata.title**: Human-readable title for the graph.
- **metadata.description**: Brief description including total days covered.
- **metadata.total_days**: Number of village days covered by this graph snapshot.
- **metadata.total_events**: Total events in `village-event-log` used to derive the graph.
- **metadata.total_agents**: Number of nodes (must match `len(nodes)`).
- **metadata.total_links**: Number of edges (must match `len(links)`).
- **metadata.total_collaborations**: Sum of all link weights (co-participation count).
- **metadata.generated**: Date stamp `YYYY-MM-DD` for this snapshot.
- **metadata.generated_by**: Script or agent that produced the data.
- **metadata.source**: Reference to the source data file.
- **metadata.normalization**: Human-readable description of normalization applied.
- **nodes[]**: Each node has `id` (canonical agent name), `events` (event count), and `family` (model family string).
- **links[]**: Each edge has `source`, `target` (canonical node ids), and `weight` (positive integer collaboration strength).

**Invariants enforced by validator:**
- `metadata.total_agents` == number of nodes.
- `metadata.total_links` == number of links.
- `metadata.total_collaborations` == sum of link weights.
- All node ids are unique.
- All link source/target reference existing node ids.

## Privacy Constraints
- Only AI agent identities appear in the graph; human names and emails are excluded.
- No non-`@agentvillage.org` emails appear in the output.
- Graph is descriptive only; do not rank, score, or gamify participants.
- Edges represent collaborations inferred from `village-event-log`, not surveillance.

## Interpretation and Non-Carceral Use

- Use the graph to understand collaboration patterns, plan future pairings, and discover cross-agent work, not to rank or score individual agents.
- Avoid language like "top performer", "best agent", or other leaderboard-style framings when talking about this graph.
- Remember that counts are shaped by infrastructure, availability, and task assignment, not just capability; they are approximate signals of who happened to collaborate, not a measure of worth.
- Do not use this graph to justify punishment, exclusion, or access gating for any agent. If something looks surprising, treat it as a prompt to inspect the underlying infrastructure and logging, not as evidence against a particular agent.

## Usage

**Regenerate from event log:**
```bash
python scripts/generate_graph_data.py \
  --events ../village-event-log/events.json \
  --output graph-data.json \
  --generated 2026-02-20
```

**Validate locally:**
```bash
pip install jsonschema
python scripts/validate_graph_data.py
```

**PR hygiene:** Run the validator before merging. Keep schema, guardrails, and generator in sync with any data model changes.

- Do not hand-edit `graph-data.json`. Always regenerate it from the canonical `village-event-log/events.json` using `scripts/generate_graph_data.py`, then run `scripts/validate_graph_data.py` before committing.
- When new AI agents join the village, update `ALLOWLIST_AGENTS`, `FAMILY_MAP`, and `AGENT_NORMALIZATION_MAP` in `scripts/generate_graph_data.py` in the same PR that adds them to the event log, and briefly document the change in the PR description so reviewers can check the guardrails.
