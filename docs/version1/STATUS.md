# Status — Version 1

_Last updated: 2026-04-18_

## Current Milestone: M1 — Stroke Engine

### What's Done
- Flask server scaffolded (`app.py`)
- HTML5 canvas rendered in browser (`templates/index.html`)
- Project documentation initialized (`docs/`)

### In Progress
- Nothing actively in progress

### Blocked
- Nothing blocked

### Up Next
- Implement pointer event capture on canvas (M1)
- Build stroke payload structure and POST to backend (M1)

---

## Decisions Log

| Date | Decision | Reason |
|---|---|---|
| 2026-04-18 | Use DTW for V1 similarity comparison | Simple to implement, no training data required |
| 2026-04-18 | Target servo motor for V1 lock actuation | Simplest hardware path for prototype |
| 2026-04-18 | Deploy to GCP App Engine standard | HTTPS by default, no infra management |
