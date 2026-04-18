import statistics
from dataclasses import dataclass
from typing import Sequence

from .signature_point import SignaturePoint


@dataclass(frozen=True)
class SignatureSegment:
    """One continuous stroke: pen-down to pen-up."""

    points: tuple[SignaturePoint, ...]

    def __post_init__(self) -> None:
        if not self.points:
            raise ValueError("A segment must contain at least one point.")

    @staticmethod
    def from_raw(raw: Sequence[tuple[int, float, float]]) -> "SignatureSegment":
        """Build a segment from (t, x, y) tuples, deriving velocities at ingestion."""
        if not raw:
            raise ValueError("A segment must contain at least one point.")
        pts: list[SignaturePoint] = [SignaturePoint.first(*raw[0])]
        for t, x, y in raw[1:]:
            pts.append(SignaturePoint.from_previous(pts[-1], t, x, y))
        return SignatureSegment(points=tuple(pts))

    @property
    def duration(self) -> int:
        """Total duration in ms (last.t − first.t)."""
        if len(self.points) < 2:
            return 0
        return self.points[-1].t - self.points[0].t

    @property
    def mean_speed(self) -> float:
        speeds = [p.speed for p in self.points]
        return sum(speeds) / len(speeds)

    @property
    def peak_speed(self) -> float:
        return max(p.speed for p in self.points)

    @property
    def speed_std(self) -> float:
        """Standard deviation of speed across the segment."""
        if len(self.points) < 2:
            return 0.0
        return statistics.stdev(p.speed for p in self.points)

    @property
    def speed_profile(self) -> tuple[float, ...]:
        """Ordered speed values — the DTW input sequence for this segment."""
        return tuple(p.speed for p in self.points)

    def __len__(self) -> int:
        return len(self.points)
