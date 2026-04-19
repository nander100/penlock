---
member: atotah
---

# Notes — atotah

# `SignaturePoint` class

One sampled position in time. The atomic unit of a signature stroke.

## Fields

| Field | Type | Description |
|---|---|---|
| `t` | int (ms) | Relative timestamp from stroke start |
| `x` | float (px) | X coordinate in raw canvas space |
| `y` | float (px) | Y coordinate in raw canvas space |
| `vx` | float (px/ms) | Instantaneous X velocity, derived from adjacent points at ingestion |
| `vy` | float (px/ms) | Instantaneous Y velocity, derived from adjacent points at ingestion |
| `speed` | float (px/ms) | Scalar magnitude of the velocity vector, derived |

## Derivation

`vx`, `vy`, and `speed` are computed at ingestion time when points are appended to a stroke — not recomputed later.

```
vx = (x[i] - x[i-1]) / (t[i] - t[i-1])
vy = (y[i] - y[i-1]) / (t[i] - t[i-1])
speed = sqrt(vx² + vy²)
```

### Boundary behaviour

| Point index | `vx`, `vy`, `speed` |
|---|---|
| 0 (first point) | 0 |
| ≥ 1 | computable |

# `StrokeSegment` class

One continuous pen-down → pen-up arc. A signature may contain multiple strokes.

## Fields

| Field | Type | Description |
|---|---|---|
| `stroke_index` | int | Order within the signature (0-indexed) |
| `points` | list[SignaturePoint] | Ordered list of sampled points (variable length) |
| `duration_ms` | int | Derived: last point `t` minus first point `t` |
| `pen_up_pause_ms` | int | Time between this stroke's last point and the next stroke's first point. Zero for the final stroke. |

## Derivation

```
duration_ms = points[-1].t - points[0].t
pen_up_pause_ms = next_stroke.points[0].t - points[-1].t
```

## Notes

- `points` is variable length — sampling rate (typically 60 Hz) and stroke duration both affect point count
- `pen_up_pause_ms` captures hesitation rhythm between strokes, a behaviorally significant featuresegment

# `SignatureSample` class

Top-level container for a single signature attempt.

## Fields

| Field | Type | Description |
|---|---|---|
| `sample_id` | UUID | Unique identifier for this sample |
| `user_id` | string | Enrolled user this belongs to |
| `mode` | enum | `ENROLL` or `VERIFY` |
| `timestamp_start` | int (ms) | Unix timestamp of first pen-down event |
| `timestamp_end` | int (ms) | Unix timestamp of final pen-up event |
| `total_duration_ms` | int | Derived: `timestamp_end - timestamp_start` |
| `strokes` | list[StrokeSegment] | Ordered list, one per pen-down → pen-up arc (variable length) |
| `canvas_width_px` | int | Viewport width at capture time |
| `canvas_height_px` | int | Viewport height at capture time |
| `device_type` | string | `mouse`, `stylus`, or `touch` |

## Derivation

```
total_duration_ms = timestamp_end - timestamp_start
```

## Notes

- `strokes` is variable length — users lift the pen a different number of times per signature
- `canvas_width_px` and `canvas_height_px` are stored for coordinate normalization downstream
- `device_type` affects whether pressure data will be available when that field is added

---

# Changes — 2026-04-18

## `svm.py` rewrite

Rewrote `svm.py` to be the single source of truth for training and prediction.

### Key changes

- Added `FEATURE_KEYS` list as the single source of truth for feature vector ordering (eliminates fragile `dict.values()` ordering)
- Added `normalize_speeds(speeds)` with empty-list guard (`min([])` raises `ValueError`)
- Added `signature_speed_profile(sig)` and `signature_acceleration_profile(sig)` — the latter returns a zero-filled fallback dict when there are no accelerations
- Added `process_signature(raw_signature) -> dict` as the single entry point for feature extraction from raw frontend JSON
- Added `to_vector(features) -> list[float]` to eliminate duplication
- Training block (runs at import time):
  - Loads `signatures.json`
  - Fits `StandardScaler` — critical for RBF kernel; unscaled `duration` in ms otherwise dominates all other features
  - Fits `OneClassSVM(kernel='rbf', nu=0.1)` on scaled data
  - Runs Leave-One-Out cross-validation and prints the false-reject rate
  - Persists model via `joblib.dump({'clf': clf, 'scaler': scaler}, 'penlock_model.pkl')`
- Added `predict_signature(raw_signature) -> str` — scales input using the fitted scaler before predicting; returns `'genuine'` or `'forged'`

> **Note:** `svm.py` trains at import time, so `signatures.json` must exist before `app.py` starts.

## `app.py` cleanup

Removed the old inline training logic from `app.py` so that `svm.py` is the single source of truth.

### Removed
- `from sklearn import svm`, `import numpy as np`, `from svm import process_signature` imports
- `clf = None` global
- `train_model()` function (used `features.values()` without scaling and a different `nu=0.25`)

### Added
- `from svm import predict_signature`

### `/verify` endpoint (simplified)

```python
@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    raw_signature = data['signature']
    if isinstance(raw_signature[0][0], list):
        raw_signature = raw_signature[0]

    is_genuine = predict_signature(raw_signature) == 'genuine'

    s = get_serial()
    if s:
        s.write(b'real\n' if is_genuine else b'fake\n')
    else:
        print("Serial not available")

    return jsonify({'genuine': is_genuine})
```