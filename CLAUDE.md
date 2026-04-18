# CLAUDE.md — PenLock

## Project Summary

PenLock is a behavioral biometric lock system. Users enroll a handwritten signature via a browser canvas over HTTPS. The temporal dynamics of the signature (position, velocity, timing) are verified on GCP. On a positive match, a WebSocket signal is sent to an Arduino which physically opens the lock.

## Repo Structure

```
PenLock/
  app.py                    # Flask entry point
  templates/
    index.html              # Signature canvas UI
  docs/
    MISSION.md              # Permanent project mission (do not edit casually)
    version1/
      ARCHITECTURE.md       # System design for V1
      PLANNING.md           # Phase breakdown and task list
      RESEARCH.md           # Background on algorithms and hardware choices
      ROADMAP.md            # Milestones and exit criteria
      STATUS.md             # Current state, decisions log
      members/
        ykim/NOTES.md       # ykim's personal working notes
        atotah/NOTES.md     # atotah's personal working notes
        alin/NOTES.md       # alin's personal working notes
  CLAUDE.md                 # This file
  README.md                 # Public-facing project overview
```

## Stack

- **Backend**: Python 3, Flask
- **Frontend**: HTML5 Canvas, vanilla JavaScript
- **Cloud**: GCP App Engine (HTTPS), Cloud Firestore (baseline storage)
- **Hardware**: Arduino (ESP8266 or ESP32) + servo motor
- **Protocol**: WebSocket (Flask-SocketIO) for lock control

## Key Concepts

- **Enrollment**: User draws signature; temporal feature vector stored as baseline
- **Verification**: User draws again; live vector compared to baseline via DTW
- **Unlock**: On match, backend sends `{ "cmd": "unlock" }` over WebSocket to Arduino
- **Temporal dynamics**: What matters is *how* the signature is drawn, not just its shape

## Development Guidelines

- Keep enrollment and verification logic separate from transport/web layer
- Feature extraction functions must be pure and testable in isolation
- Never store raw stroke data after feature extraction — only the feature vector
- All user-facing endpoints must be HTTPS only (App Engine enforces this in production)
- The DTW threshold is a tunable parameter — do not hardcode it deep in logic

## Documentation Convention — Member Folders

Each team member has a personal folder under `docs/version1/members/<handle>/`. Members only write inside their own folder. This prevents merge conflicts on shared docs — never edit another member's folder.

Current members: `ykim`, `atotah`, `alin`.

To add a new member: create `docs/version1/members/<handle>/NOTES.md` and add them to this list.

---

## Current Focus

M1 — Stroke Engine: implement pointer event capture on the canvas and build the stroke payload pipeline.

See `docs/version1/PLANNING.md` for the full task breakdown.
