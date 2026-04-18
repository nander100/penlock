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
- JavaScript captures pointer events: `(x, y, timestamp)` on each `pointermove` / `pointerdown` / `pointerup`
- Computes per-sample velocity from consecutive coordinate deltas and time deltas
- On submission, sends a structured stroke payload to the backend

**Stroke payload shape:**
```json
{
  "strokes": [
    {
      "points": [
        { "x": 120, "y": 45, "t": 0, "vx": 0, "vy": 0 },
        { "x": 125, "y": 48, "t": 16, "vx": 312.5, "vy": 187.5 }
      ]
    }
  ]
}
```

---

### 2. Backend (GCP — Flask)

Responsibilities:
- Serve the HTTPS frontend
- Accept enrollment requests (store baseline feature vector)
- Accept verification requests (compare live vector against baseline)
- On positive match, push unlock signal via WebSocket to the registered Arduino

**Endpoints (planned):**

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Serve frontend |
| `POST` | `/enroll` | Store baseline signature |
| `POST` | `/verify` | Verify signature, trigger lock on match |
| `WS` | `/lock` | WebSocket connection from Arduino |

---

### 3. Signature Verification

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

### 4. WebSocket → Arduino

- Arduino maintains a persistent WebSocket connection to the GCP backend
- On verification success, backend sends `{ "cmd": "unlock" }`
- Arduino receives the message, actuates the servo/relay for a fixed duration, then re-locks

---

## Data Flow: Verification

```
1. User draws signature in browser
2. JS captures strokes with timestamps and velocities
3. Browser POSTs stroke payload to /verify over HTTPS
4. Backend extracts feature vector from payload
5. Backend compares feature vector against stored baseline
6. If match: backend sends {"cmd": "unlock"} over WebSocket to Arduino
7. Arduino actuates lock
8. Backend returns 200 + result to browser
```

---

## Deployment Target

- GCP App Engine (standard environment, Python 3.x)
- Arduino connected via local network with outbound WebSocket to GCP
