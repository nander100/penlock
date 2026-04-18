# Research — Version 1

## Behavioral Biometrics: Online Signature Verification

Online signature verification captures the **process** of signing, not just the final image. This is called an "online" (dynamic) approach as opposed to "offline" (static image comparison).

### Key Features Used in the Literature

| Feature | Description |
|---|---|
| Velocity | Speed of pen at each point |
| Acceleration | Rate of change of speed |
| Stroke count | Number of pen-down/pen-up events |
| Duration | Total time to complete signature |
| Pressure | Force applied (if device supports it) |
| Pen angle | Stylus tilt (if device supports it) |
| Path curvature | Direction changes along the stroke |

For V1, PenLock targets: **velocity, duration, stroke count, and normalized path** — all derivable from standard browser pointer events without pressure or angle sensors.

---

## Comparison Algorithms

### Dynamic Time Warping (DTW)
- Aligns two time series of different lengths by finding the optimal warp path
- Well-suited for speed profile sequences which vary in length and tempo between signings
- Simple to implement, interpretable threshold
- Reference: Sakoe & Chiba (1978)

### Edit Distance on Real Sequences (EDR)
- More robust to noise than DTW
- Higher implementation complexity

### Learned Embeddings (Siamese Networks)
- Higher accuracy but requires training data per user
- Not feasible for V1 with a single-device prototype

**Decision for V1: DTW on velocity profile sequences.**

---

## Replay Attack Considerations

A recorded stroke sequence (captured from a legitimate signing session) could theoretically be replayed. Mitigations:

1. **Timestamp window** — reject verifications where the session timestamp is outside a short window of the server time (prevents old recordings)
2. **Nonce** — server issues a one-time nonce per session; signature payload must include it
3. **Behavioral noise** — natural variation in genuine signings means a perfect replay of one session would itself be flagged as anomalous if the threshold is tight enough

V1 targets mitigation #1 as a minimum viable defense.

---

## WebSocket for Lock Control

WebSocket is preferred over polling because:
- Sub-100ms latency from verification to unlock signal
- Persistent connection avoids TCP handshake overhead per event
- Arduino WebSocket libraries (e.g., `arduinoWebSockets` by Links2004) are mature and well-documented

### Arduino Libraries Under Consideration
- `arduinoWebSockets` (Links2004) — widely used, supports SSL with ESP8266/ESP32
- `WebSockets2_Generic` — broader board support

---

## Hardware

### Lock Actuation Options
| Option | Pros | Cons |
|---|---|---|
| Servo motor | Simple, precise, quiet | Limited torque |
| Relay + solenoid lock | Standard door hardware compatible | Requires 12V supply |
| Relay + electric strike | Clean installation | Higher cost |

**V1 target: servo motor** for prototype simplicity.

---

## GCP Services

| Service | Use |
|---|---|
| App Engine (standard) | Host Flask backend, auto-scales, HTTPS by default |
| Cloud Firestore | Store per-user baseline feature vectors |
| Cloud Logging | Audit trail of verification events |

---

## References

- Impedovo, D., & Pirlo, G. (2008). Automatic Signature Verification: The State of the Art. *IEEE Transactions on Systems, Man, and Cybernetics*.
- Sakoe, H., & Chiba, S. (1978). Dynamic programming algorithm optimization for spoken word recognition. *IEEE Transactions on Acoustics, Speech, and Signal Processing*.
- Links2004 arduinoWebSockets: https://github.com/Links2004/arduinoWebSockets
