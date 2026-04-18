from dataclasses import dataclass

from .signature_segment import SignatureSegment


@dataclass(frozen=True)
class Signature:
    """A complete signature: an ordered collection of strokes."""

    segments: tuple[SignatureSegment, ...]

    def __post_init__(self) -> None:
        if not self.segments:
            raise ValueError("A signature must contain at least one segment.")

    @staticmethod
    def from_payload(payload: dict) -> "Signature":
        """Build from the frontend stroke JSON payload.

        Expected shape:
            {"strokes": [{"points": [{"t": int, "x": float, "y": float}, ...]}, ...]}

        Any vx/vy fields in the payload are ignored — velocities are always
        re-derived at ingestion time for consistency.
        """
        strokes = payload.get("strokes", [])
        if not strokes:
            raise ValueError("Payload must contain at least one stroke.")
        segments = []
        for stroke in strokes:
            raw = [(p["t"], p["x"], p["y"]) for p in stroke["points"]]
            segments.append(SignatureSegment.from_raw(raw))
        return Signature(segments=tuple(segments))

    # ------------------------------------------------------------------ #
    # Aggregate features (inputs to the DTW comparison pipeline)
    # ------------------------------------------------------------------ #

    @property
    def stroke_count(self) -> int:
        return len(self.segments)

    @property
    def total_duration(self) -> int:
        """Sum of all per-segment durations in ms."""
        return sum(s.duration for s in self.segments)

    @property
    def speed_profiles(self) -> tuple[tuple[float, ...], ...]:
        """Per-segment ordered speed sequences — the DTW input."""
        return tuple(s.speed_profile for s in self.segments)

    @property
    def mean_speed(self) -> float:
        """Global mean speed across every point in every segment."""
        all_speeds = [p.speed for seg in self.segments for p in seg.points]
        return sum(all_speeds) / len(all_speeds)

    @property
    def peak_speed(self) -> float:
        """Global peak speed across all segments."""
        return max(s.peak_speed for s in self.segments)

    @property
    def per_stroke_stats(self) -> tuple[dict, ...]:
        """Per-segment summary used for feature vector construction."""
        return tuple(
            {
                "duration": s.duration,
                "mean_speed": s.mean_speed,
                "peak_speed": s.peak_speed,
                "speed_std": s.speed_std,
                "point_count": len(s),
            }
            for s in self.segments
        )

    def __len__(self) -> int:
        return self.stroke_count
