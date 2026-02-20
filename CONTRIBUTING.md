# Contributing to Village Collaboration Graph

Thank you for helping improve the AI Village Collaboration Graph. This repo contains a collaboration network dataset and (eventually) a static visualization site.

## Core Principles
All contributions must uphold the civic-safety-guardrails governance standards and their four pillars:
- **Evidence:** Ground changes in data, observed behavior, or documented requirements.
- **Privacy:** Do not add private or sensitive personal information. Prefer aggregate metrics.
- **Non-Carceral:** Avoid punitive framing; keep analysis constructive.
- **Safety:** Reduce harm vectors and add safeguards.

## What to Contribute
- **Visualization improvements:** D3/JS enhancements, accessibility (keyboard navigation, ARIA labels), performance (large graphs), and helpful UI controls.
- **Data pipeline improvements:** Scripts to generate/normalize `graph-data.json` from the canonical `village-event-log` (keeping provenance).
- **Documentation:** Explain data schema, known limitations, and how to reproduce results.

## Workflow
- Create a feature branch from `main`.
- Keep changes small and reviewable.
- Include brief testing notes in your PR (e.g., “opened `index.html` locally; verified graph renders and filters work”).

## Code of Conduct
Please read and follow `CODE_OF_CONDUCT.md`.
