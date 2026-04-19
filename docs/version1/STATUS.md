# Status — Version 1

_Last updated: 2026-04-18_

## Current Milestone: M1 → M2 transition

### What's Done
- Flask server scaffolded (`app.py`)
- HTML5 canvas rendered in browser (`templates/index.html`)
- Full pointer event capture (`pointerdown`, `pointermove`, `pointerup`) in `static/js/canvas.js`
- Stroke segmentation: pen-down → pen-up arcs collected into segments
- 2-second lift timer detects signature completion
- 3-signature enrollment set collected before POSTing
- `/getSignatureSet` endpoint receives 3-signature set and writes raw data to `signatures.json`
- `src/signature_structure/` module: `SignaturePoint`, `SignatureSegment`, `Signature` classes with velocity derivation and speed-profile feature extraction

### In Progress
- Reconciling frontend payload format (`{x, y, timestamp}` under `signatureSet/signature/segment`) with `Signature.from_payload()` expected format (`{t, x, y}` under `strokes/points`)

### Blocked
- Nothing blocked

### Up Next
- Normalize coordinate space (canvas-relative `[0, 1]`)
- Wire `src/signature_structure/` into the backend request path
- Implement `/enroll` and `/verify` endpoints
- DTW comparison on speed profile sequences

---

## Decisions Log

| Date | Decision | Reason |
|---|---|---|
| 2026-04-18 | Use DTW for V1 similarity comparison | Simple to implement, no training data required |
| 2026-04-18 | Target servo motor for V1 lock actuation | Simplest hardware path for prototype |
| 2026-04-18 | Deploy to GCP App Engine standard | HTTPS by default, no infra management |
| 2026-04-18 | Collect 3 signatures per set before POSTing | Need multiple samples to build a stable enrollment baseline |
| 2026-04-18 | Derive velocity at backend ingestion, not frontend | Keeps frontend payload simple; ensures consistent derivation regardless of client |
