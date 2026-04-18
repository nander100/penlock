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