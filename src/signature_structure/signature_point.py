import math
from dataclasses import dataclass


@dataclass(frozen=True)
class SignaturePoint:
    t: int        # ms, relative to stroke start
    x: float      # px, raw canvas space
    y: float      # px, raw canvas space
    vx: float     # px/ms, derived at ingestion
    vy: float     # px/ms, derived at ingestion
    speed: float  # px/ms, scalar magnitude

    @staticmethod
    def first(t: int, x: float, y: float) -> "SignaturePoint":
        """Create the first point of a stroke (velocity is zero)."""
        return SignaturePoint(t=t, x=x, y=y, vx=0.0, vy=0.0, speed=0.0)

    @staticmethod
    def from_previous(
        prev: "SignaturePoint", t: int, x: float, y: float
    ) -> "SignaturePoint":
        """Create a subsequent point, deriving velocity from the previous point."""
        dt = t - prev.t
        if dt == 0:
            vx, vy = 0.0, 0.0
        else:
            vx = (x - prev.x) / dt
            vy = (y - prev.y) / dt
        speed = math.sqrt(vx * vx + vy * vy)
        return SignaturePoint(t=t, x=x, y=y, vx=vx, vy=vy, speed=speed)
