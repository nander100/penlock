# Roadmap — Version 1

## Milestone Overview

| Milestone | Description | Status |
|---|---|---|
| M0 — Scaffold | Flask server + canvas in browser | Done |
| M1 — Stroke Engine | Full temporal capture in browser | In progress |
| M2 — Backend Verification | Enrollment + DTW-based verify | Not started |
| M3 — Arduino Integration | WebSocket unlock signal to hardware | Not started |
| M4 — GCP Deployment | Cloud-hosted, HTTPS, Firestore | Not started |
| M5 — Hardening | Replay defense, rate limiting, audit log | Not started |

---

## M1 — Stroke Engine

**Deliverable:** Browser captures `(x, y, t, vx, vy)` per sample, packages into JSON, POSTs to backend.

Tasks:
- Wire `pointerdown` / `pointermove` / `pointerup` events on canvas
- Record timestamp on each sample
- Compute velocity from consecutive samples
- Normalize coordinates to canvas-relative `[0, 1]` range
- Build stroke payload and POST to `/enroll` or `/verify`

Exit criteria: Backend logs a well-formed stroke payload for a drawn signature.

---

## M2 — Backend Verification

**Deliverable:** `/enroll` stores a baseline; `/verify` returns `match: true/false`.

Tasks:
- Extract feature vector from stroke payload (duration, speed profile, stroke count, normalized path)
- Store baseline per user ID (in-memory for local dev, Firestore for GCP)
- Implement DTW comparison on speed profile sequences
- Tune accept/reject threshold on real signing samples
- Return structured response: `{ "match": bool, "score": float }`

Exit criteria: Genuine signature verifies successfully; a different person's signature is rejected.

---

## M3 — Arduino Integration

**Deliverable:** Lock opens within 500ms of a verified signature.

Tasks:
- Set up Flask-SocketIO WebSocket server
- Write Arduino sketch: connect to WebSocket, listen for `{ "cmd": "unlock" }`, actuate servo for 5s then re-lock
- Test end-to-end on local network: sign → verify → unlock

Exit criteria: Physical lock actuates reliably on positive verification; does not actuate on failed verification.

---

## M4 — GCP Deployment

**Deliverable:** System runs fully in the cloud; Arduino connects over the internet.

Tasks:
- `app.yaml` for App Engine deployment
- Migrate baseline storage from in-memory to Cloud Firestore
- Configure WebSocket support on App Engine (Flexible environment if needed)
- Update Arduino sketch with GCP endpoint URL
- Verify HTTPS enforced end-to-end

Exit criteria: Full flow works with Arduino connecting to GCP endpoint over the internet.

---

## M5 — Hardening

**Deliverable:** System is resistant to basic replay and brute-force attacks.

Tasks:
- Timestamp window validation (reject payloads older than 30s)
- Rate limiting on `/verify` (max 5 attempts per minute per IP)
- Audit log: each verification attempt logged to Cloud Logging with result and score
- Threshold review: measure FAR/FRR with test samples and adjust

Exit criteria: Replay of a recorded session is rejected; excessive failed attempts are rate-limited.

---

## Beyond V1

After M5, the following are candidates for V2:
- Multi-sample enrollment (average over 3+ signings for a more stable baseline)
- Learned embedding model (Siamese network) for higher accuracy
- Mobile web support (touch events, pressure via PointerEvent API)
- Admin dashboard: view verification history, manage enrolled users
- Multi-lock support: one backend, multiple Arduino endpoints
