# Architecture — Version 1

## System Diagram

```
[User Browser]
     |
     | HTTPS (signature stroke data)
     v
[GCP Backend — Flask / Verification Service]
     |
     | WebSocket
     v
[Arduino]
     |
     v
[Physical Lock]
```

---

## Layers

### 1. Frontend (Browser)

- HTML5 Canvas rendered over HTTPS
- JavaScript (`static/js/canvas.js`) captures pointer events: `(x, y, timestamp)` on each `pointermove` / `pointerdown` / `pointerup`
- Segments strokes by pen-lift: each pen-down → pen-up arc is one segment
- Detects signature completion via a 2-second lift timer
- Collects 3 signature attempts into a set, then POSTs the set to `/getSignatureSet`
- Velocity (`vx`, `vy`, `speed`) is **not computed on the frontend** — it is derived at backend ingestion time

**Frontend payload shape (sent to `/getSignatureSet`):**
```json
{
  "signatureSet": [
    [
      [
        { "x": 120.0, "y": 45.0, "timestamp": 1776551432826 },
        { "x": 125.0, "y": 48.0, "timestamp": 1776551432842 }
      ]
    ]
  ]
}
```

Structure: `signatureSet [ signature [ segment [ point{x, y, timestamp} ] ] ]`

---

### 2. Backend (GCP — Flask)

Responsibilities:
- Serve the HTTPS frontend
- Accept enrollment requests (store baseline feature vector)
- Accept verification requests (compare live vector against baseline)
- On positive match, push unlock signal via WebSocket to the registered Arduino

**Endpoints:**

| Method | Path | Status | Purpose |
|---|---|---|---|
| `GET` | `/` | Live | Serve frontend |
| `POST` | `/getSignatureSet` | Live | Receive 3-signature set; currently writes raw data to `signatures.json` |
| `POST` | `/enroll` | Planned | Store baseline feature vector per user |
| `POST` | `/verify` | Planned | Compare live signature against baseline, trigger lock on match |
| `WS` | `/lock` | Planned | WebSocket connection from Arduino |

---

### 3. Signature Structure Module (`src/signature_structure/`)

Python dataclasses that model and process raw stroke data. Built but not yet wired to any endpoint.

| Class | File | Role |
|---|---|---|
| `SignaturePoint` | `signature_point.py` | Atomic sample: `(t, x, y, vx, vy, speed)`. Velocity derived from adjacent points at ingestion. |
| `SignatureSegment` | `signature_segment.py` | One pen-down→pen-up arc. Exposes `duration`, `mean_speed`, `peak_speed`, `speed_std`, `speed_profile`. |
| `Signature` | `signature.py` | Full multi-segment signature. Exposes `stroke_count`, `total_duration`, `speed_profiles`, `mean_speed`, `peak_speed`, `per_stroke_stats`. Parses from a `{"strokes": [{"points": [...]}]}` payload via `Signature.from_payload()`. |

> **Open gap:** the frontend currently sends `{x, y, timestamp}` under `signatureSet/signature/segment` keys, but `Signature.from_payload()` expects `{t, x, y}` under `strokes/points` keys. These must be reconciled before the module can be wired to the backend.

---

### 4. Signature Verification

Feature extraction from raw stroke data:
- Total stroke duration
- Per-stroke speed profile (mean, std dev, peak)
- Stroke count and ordering
- Normalized path shape (DTW-compatible)

Comparison:
- Dynamic Time Warping (DTW) on speed profile sequences
- Euclidean distance on normalized path
- Threshold-based accept/reject decision

---

### 5. WebSocket → Arduino

- Arduino maintains a persistent WebSocket connection to the GCP backend
- On verification success, backend sends `{ "cmd": "unlock" }`
- Arduino receives the message, actuates the servo/relay for a fixed duration, then re-locks

---

## Data Flow: Verification (target — not fully wired yet)

```
1. User draws signature in browser
2. JS captures strokes: (x, y, timestamp) per point, grouped into segments and signatures
3. After 3 signatures collected, browser POSTs signatureSet to /enroll or /verify over HTTPS
4. Backend ingests payload: derives (vx, vy, speed) at ingestion via SignaturePoint
5. Backend extracts feature vector via Signature / SignatureSegment
6. Backend compares feature vector against stored baseline (DTW on speed profiles)
7. If match: backend sends {"cmd": "unlock"} over WebSocket to Arduino
8. Arduino actuates lock
9. Backend returns 200 + result to browser
```

**Current state:** Steps 1–3 post to `/getSignatureSet` which writes raw data to `signatures.json`. Steps 4–9 are not yet wired.

---

## Deployment Target

- GCP App Engine (standard environment, Python 3.x)
- Arduino connected via local network with outbound WebSocket to GCP
