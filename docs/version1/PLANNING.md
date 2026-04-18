# Planning — Version 1

## Goal

Deliver a working end-to-end prototype: a user can enroll their signature via browser, then verify it to physically open a lock via Arduino.

---

## Phases

### Phase 0 — Scaffold (current)
- [x] Flask server running locally
- [x] Canvas rendered in browser
- [ ] Basic stroke capture (x, y, t) on canvas events
- [ ] Display captured stroke data in console for inspection

### Phase 1 — Stroke Engine
- [ ] Implement full stroke capture: `pointerdown`, `pointermove`, `pointerup`
- [ ] Compute velocity at each sample point
- [ ] Normalize coordinate space (canvas-relative)
- [ ] Package strokes into JSON payload
- [ ] POST payload to backend `/enroll` and `/verify`

### Phase 2 — Backend Verification
- [ ] Flask endpoint `/enroll` — receive and store baseline feature vector
- [ ] Flask endpoint `/verify` — receive live vector, run comparison
- [ ] Feature extraction: duration, speed profile, stroke count, normalized path
- [ ] DTW-based similarity comparison
- [ ] Threshold tuning (false accept rate vs. false reject rate)

### Phase 3 — WebSocket + Arduino
- [ ] Flask WebSocket server (Flask-SocketIO or raw websockets)
- [ ] Arduino WebSocket client sketch
- [ ] Unlock signal: `{ "cmd": "unlock" }`
- [ ] Arduino actuates servo/relay on unlock signal, re-locks after timeout

### Phase 4 — GCP Deployment
- [ ] Deploy Flask app to GCP App Engine
- [ ] Move baseline storage to Cloud Firestore or Cloud Storage
- [ ] HTTPS enforced by default on App Engine
- [ ] Arduino connects to GCP WebSocket endpoint

### Phase 5 — Hardening
- [ ] Rate limiting on `/verify`
- [ ] Replay attack mitigation (nonce or timestamp window)
- [ ] Logging and audit trail per verification attempt
- [ ] Threshold calibration with real user data

---

## Open Questions

- What similarity metric gives the best balance of security vs. usability? (DTW vs. learned embedding)
- How many enrollment samples are needed for a stable baseline?
- Should the Arduino re-lock after a fixed timeout or on an explicit lock signal?
- What happens if the WebSocket connection drops during a verification event?
