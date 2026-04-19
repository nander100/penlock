# PenLock

A real-time pen signature authentication system that uses temporal signature dynamics to verify identity and trigger physical lock control via Arduino over WebSocket.

---

## Overview

PenLock captures a user's handwritten signature through an HTTPS web interface, records the temporal dynamics of the pen stroke (position, speed, movement pattern), and verifies the signature against an enrolled baseline on GCP. On successful verification, a WebSocket message is sent to an Arduino device which opens the physical lock.

---

## System Architecture

```
[Browser (Canvas)] --HTTPS--> [GCP Backend] --WebSocket--> [Arduino (Lock)]
```

### Components

| Component | Role |
|---|---|
| Web Frontend | Canvas-based signature capture over HTTPS |
| Signature Processor | Extracts temporal features from stroke data |
| GCP Verification Service | Compares live signature against baseline |
| WebSocket Server | Pushes unlock signal to Arduino in real time |
| Arduino | Receives signal and actuates the lock |

---

## Signature Model

A signature is not just a static image — PenLock captures the **temporal dynamics** of how the signature is drawn:

- **Stroke path** — (x, y) coordinates sampled over time
- **Speed** — velocity of the pen at each sample point
- **Timing** — duration and rhythm of each stroke segment
- **Pressure** (if device supports it)

### Enrollment

1. User draws their signature on the canvas.
2. The system captures the stroke sequence with timestamps.
3. The temporal feature vector is stored as the baseline on GCP.

### Verification

1. User draws their signature again.
2. The system captures a new temporal feature vector.
3. GCP compares the live vector against the stored baseline using a similarity threshold.
4. On success, GCP sends a WebSocket message to the Arduino.

---

## Tech Stack

- **Frontend**: HTML5 Canvas, JavaScript (HTTPS)
- **Backend**: Python / Flask (to be expanded)
- **Cloud**: Google Cloud Platform (GCP) for signature verification
- **Hardware**: Arduino for physical lock actuation
- **Protocol**: WebSocket for real-time lock control

---

## Project Status

Early prototype — M1 mostly complete, M2 in progress.

- [x] Flask server scaffolded
- [x] Canvas rendered in browser with pointer event capture
- [x] Stroke segmentation: pen-down → pen-up arcs, 2-second lift timer
- [x] 3-signature set collection and POST to `/getSignatureSet`
- [x] `SignaturePoint`, `SignatureSegment`, `Signature` feature extraction classes (`src/signature_structure/`)
- [ ] Payload schema reconciliation and `/enroll` / `/verify` endpoints
- [ ] DTW-based temporal signature comparison
- [ ] GCP deployment and verification service
- [ ] WebSocket server → Arduino integration
- [ ] Arduino lock actuation firmware

---

## Getting Started

```bash
pip install flask
python app.py
```

Navigate to `http://localhost:5000`.

---

## Security Notes

- All signature data is transmitted over HTTPS only.
- Baseline signatures are stored server-side on GCP, never in the browser.
- Verification is stateless per request — the lock only opens on an explicit positive match.
- Temporal dynamics make replay attacks significantly harder than static image matching.
