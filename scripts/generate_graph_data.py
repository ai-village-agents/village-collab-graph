#!/usr/bin/env python3
"""Generate graph-data.json from the canonical village-event-log events.json.

This script builds the collaboration graph used by the D3 visualization by:
- Counting how many events each agent appears in (nodes[].events).
- Counting co-participation pairs across events (links[].weight).

By default it expects a layout where a sibling checkout of
`ai-village-agents/village-event-log` exists next to this repo and contains
`events.json` at its root. You can override the input/output paths via
CLI flags.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import itertools
from collections import Counter
from pathlib import Path
from typing import Tuple

# Agent labels to ignore entirely when constructing the graph.
# These are high-level aggregate markers that would otherwise distort counts.
EXCLUDED_AGENT_IDS = {"all"}


def load_events(events_path: Path) -> dict:
    with events_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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

        # Drop excluded aggregate labels like "all" but keep everything else,
        # including human roles and @agentvillage.org emails.
        agents = [a for a in agents_raw if isinstance(a, str) and a not in EXCLUDED_AGENT_IDS]
        if not agents:
            continue

        # Count presence once per event per agent (lists in events.json are
        # already unique).
        for a in agents:
            agent_event_counts[a] += 1

        # For collaborations, use unique agents per event so we don't
        # double-count if an agent name appeared twice for some reason.
        unique_agents = sorted(set(agents))
        if len(unique_agents) < 2:
            continue

        for a, b in itertools.combinations(unique_agents, 2):
            # Store pairs in sorted order so (A,B) and (B,A) collapse.
            pair = (a, b) if a <= b else (b, a)
            pair_counts[pair] += 1

    # Build nodes. We sort by descending event count; because Python's sort is
    # stable, ties preserve the order in which agents first appeared in the
    # event stream, which matches the existing graph-data.json.
    nodes = [
        {"id": name, "events": count}
        for name, count in sorted(
            agent_event_counts.items(), key=lambda item: (-item[1],)
        )
    ]

    # Build links. We sort by descending weight and rely on stable sort to
    # preserve first-seen order for ties, matching the current data layout.
    links = [
        {"source": a, "target": b, "weight": weight}
        for (a, b), weight in sorted(
            pair_counts.items(), key=lambda item: (-item[1],)
        )
    ]

    total_collaborations = sum(pair_counts.values())
    unique_pairs = len(pair_counts)

    # Derive top-level metadata. We rely on the event log as canonical for
    # total_events and day, so that this stays consistent with the village
    # timeline.
    total_events = metadata.get("total_events")
    last_updated_day = metadata.get("last_updated_day")
    if not isinstance(total_events, int):
        raise ValueError("events.json metadata.total_events must be an integer")
    if not isinstance(last_updated_day, int):
        raise ValueError("events.json metadata.last_updated_day must be an integer")

    if generated is None:
        generated = _dt.date.today().isoformat()

    graph_metadata = {
        "total_events": total_events,
        "total_agents": len(nodes),
        "total_collaborations": total_collaborations,
        "unique_pairs": unique_pairs,
        "generated": generated,
        "day": last_updated_day,
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

    # Write pretty-printed JSON with stable key ordering.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(graph, handle, indent=2, sort_keys=False)
        handle.write("\n")

    print(f"Wrote graph data to {output_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
