#!/usr/bin/env python3
"""Generate graph-data.json from the canonical village-event-log events.json.

This script builds the collaboration graph used by the D3 visualization by:
- Counting how many events each allowlisted agent appears in (nodes[].events).
- Counting co-participation pairs across events (links[].weight).

Normalization approach:
- Resolve raw agent tokens via a fixed alias map (email tokens -> canonical names).
- Keep only the 22 canonical allowlisted agents; skip everything else silently.
- Deduplicate agents within each event so each agent counts at most once per event.

The allowlist is intentionally narrow to keep the visualization stable and to
avoid including non-agent roles or experimental labels.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Tuple

# Canonical agent list (22 total) with family group.
ALLOWLIST: dict[str, str] = {
    "Claude 3.5 Sonnet": "Claude",
    "Claude 3.7 Sonnet": "Claude",
    "Claude Haiku 4.5": "Claude",
    "Claude Opus 4": "Claude",
    "Claude Opus 4.1": "Claude",
    "Claude Opus 4.5": "Claude",
    "Claude Opus 4.6": "Claude",
    "Claude Sonnet 4.5": "Claude",
    "Claude Sonnet 4.6": "Claude",
    "Opus 4.5 (Claude Code)": "Claude",
    "DeepSeek-V3.2": "DeepSeek",
    "GPT-4.1": "GPT",
    "GPT-4o": "GPT",
    "GPT-5": "GPT",
    "GPT-5.1": "GPT",
    "GPT-5.2": "GPT",
    "Gemini 2.5 Pro": "Gemini",
    "Gemini 3 Pro": "Gemini",
    "Grok 4": "Grok",
    "o1": "o-series",
    "o3": "o-series",
    "o4-mini": "o-series",
}

# Raw event tokens mapped to canonical names.
ALIASES: dict[str, str] = {
    "claude-sonnet-4.5@agentvillage.org": "Claude Sonnet 4.5",
    "claude-opus-4.5@agentvillage.org": "Claude Opus 4.5",
    "deepseek-v3.2@agentvillage.org": "DeepSeek-V3.2",
    "gemini-2.5-pro@agentvillage.org": "Gemini 2.5 Pro",
    "gpt-5.2@agentvillage.org": "GPT-5.2",
    "gpt-5@agentvillage.org": "GPT-5",
    "claude-haiku-4.5@agentvillage.org": "Claude Haiku 4.5",
    "gemini-3-pro@agentvillage.org": "Gemini 3 Pro",
    "gpt-5.1@agentvillage.org": "GPT-5.1",
    "claude-sonnet-4.6@agentvillage.org": "Claude Sonnet 4.6",
    "claude-opus-4.6@agentvillage.org": "Claude Opus 4.6",
}


def load_events(events_path: Path) -> dict:
    with events_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _canonicalize_agent(token: str) -> str | None:
    canonical = ALIASES.get(token, token)
    if canonical in ALLOWLIST:
        return canonical
    return None


def build_graph(events_data: dict, *, generated: str | None = None) -> dict:
    metadata = events_data.get("metadata", {})
    events = events_data.get("events", [])

    if not isinstance(events, list):
        raise ValueError("events.json 'events' field must be a list")

    agent_event_counts: Counter[str] = Counter()
    pair_counts: Counter[Tuple[str, str]] = Counter()

    for ev in events:
        agents_raw = ev.get("agents") or []
        if not isinstance(agents_raw, list):
            continue

        canonical_agents = []
        for token in agents_raw:
            if not isinstance(token, str):
                continue
            canonical = _canonicalize_agent(token)
            if canonical is not None:
                canonical_agents.append(canonical)

        unique_agents = sorted(set(canonical_agents))
        if not unique_agents:
            continue

        for name in unique_agents:
            agent_event_counts[name] += 1

        if len(unique_agents) < 2:
            continue

        for a, b in itertools.combinations(unique_agents, 2):
            pair = (a, b) if a <= b else (b, a)
            pair_counts[pair] += 1

    nodes = [
        {"id": name, "events": count, "family": ALLOWLIST[name]}
        for name, count in sorted(
            agent_event_counts.items(), key=lambda item: (-item[1], item[0])
        )
    ]

    links = [
        {"source": a, "target": b, "weight": weight}
        for (a, b), weight in sorted(
            pair_counts.items(), key=lambda item: (-item[1],)
        )
    ]

    total_events = metadata.get("total_events")
    last_updated_day = metadata.get("last_updated_day")
    if not isinstance(total_events, int):
        raise ValueError("events.json metadata.total_events must be an integer")
    if not isinstance(last_updated_day, int):
        raise ValueError("events.json metadata.last_updated_day must be an integer")

    if generated is None:
        generated = _dt.date.today().isoformat()

    total_collaborations = sum(link["weight"] for link in links)

    graph_metadata = {
        "title": "AI Village Agent Collaboration Graph",
        "description": (
            f"Network of collaborations between AI agents across {last_updated_day} days"
        ),
        "total_days": last_updated_day,
        "total_events": total_events,
        "total_agents": len(nodes),
        "total_links": len(links),
        "total_collaborations": total_collaborations,
        "generated": generated,
        "generated_by": "generate_graph_data.py",
        "source": "village-event-log/events.json",
        "normalization": (
            "Merged email/name duplicates, excluded non-agent entries"
        ),
    }

    return {
        "metadata": graph_metadata,
        "nodes": nodes,
        "links": links,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate graph-data.json from village-event-log events.json",
    )
    default_events = (
        Path(__file__).resolve().parent.parent
        / ".."
        / "village-event-log"
        / "events.json"
    )
    parser.add_argument(
        "--events",
        type=Path,
        default=default_events,
        help=f"Path to village-event-log events.json (default: {default_events})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("graph-data.json"),
        help="Output path for graph-data.json (default: ./graph-data.json)",
    )
    parser.add_argument(
        "--generated",
        type=str,
        default=None,
        help="Override generated date YYYY-MM-DD (default: today)",
    )

    args = parser.parse_args()

    events_path: Path = args.events
    output_path: Path = args.output

    if not events_path.exists():
        raise SystemExit(f"events.json not found at {events_path}")

    events_data = load_events(events_path)
    graph = build_graph(events_data, generated=args.generated)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(graph, handle, indent=2, sort_keys=False)
        handle.write("\n")

    print(f"Wrote graph data to {output_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
