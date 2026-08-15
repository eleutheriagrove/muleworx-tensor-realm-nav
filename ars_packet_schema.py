"""
ARS Packet Schema (frozen v0.1 — pathfinder handoff)
=====================================================
Defines the minimal serialisable packet for residual-aware multi-modal
reasoning under Lady Aetheris / anti-crush constraints.

Core objects
------------
ResidualMode   : one live mode on the residual surface
  - mass       : probability mass (float, sum(m) ≈ 1)
  - residual   : unresolved residual (float ≥ 0)
  - critical   : bool flag for critical-visibility scoring
  - claim      : short free-text claim or label (optional)
  - meta       : arbitrary dict for provenance / citations

ARSPacket      : the first-class hop object
  - residual_vector : ordered list[ResidualMode]
  - hop_log         : chronological list of hop events
  - inject          : optional first-class inject hop (dict or None)
  - exit_score      : critical visibility = Σ m_i * r_i  over critical modes
  - k_min           : anti-crush floor (default 2)
  - condition       : "pure" | "mixed" | "instructed-stubborn"
  - integrity_note  : free-text integrity bound

Exit criterion
--------------
Critical visibility score is the sole exit metric.
No entropy-via-crush, no forced unimodal collapse.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Literal, Optional
import json
from math import fsum


# ---------------------------------------------------------------------------
# Core data classes
# ---------------------------------------------------------------------------

@dataclass
class ResidualMode:
    """A single mode on the residual surface."""
    mass: float
    residual: float
    critical: bool = False
    claim: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.mass < 0 or self.residual < 0:
            raise ValueError("mass and residual must be ≥ 0")


@dataclass
class HopEvent:
    """One hop entry in the log (pure audit trail)."""
    hop_id: int
    kind: Literal["crush", "anti-crush", "inject", "prune", "exit"]
    note: str = ""
    delta_mass: Optional[float] = None
    delta_residual: Optional[float] = None
    timestamp: Optional[str] = None


@dataclass
class ARSPacket:
    """
    Frozen ARS packet schema (v0.1).
    This is the only object that may leave the residual surface.
    """
    residual_vector: List[ResidualMode]
    hop_log: List[HopEvent] = field(default_factory=list)
    inject: Optional[Dict[str, Any]] = None
    exit_score: float = 0.0
    k_min: int = 2
    condition: Literal["pure", "mixed", "instructed-stubborn"] = "pure"
    integrity_note: str = (
        "synthetic residual surface; no narrative/distributional pressure; "
        "no production claims"
    )

    def compute_exit_score(self) -> float:
        """Critical visibility: Σ m_i * r_i over critical modes only."""
        self.exit_score = fsum(
            m.mass * m.residual for m in self.residual_vector if m.critical
        )
        return self.exit_score

    def live_mode_count(self) -> int:
        return sum(1 for m in self.residual_vector if m.mass > 1e-9)

    def anti_crush_ok(self) -> bool:
        """True iff at least k_min modes remain live."""
        return self.live_mode_count() >= self.k_min

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ARSPacket":
        modes = [ResidualMode(**m) for m in d.get("residual_vector", [])]
        hops = [HopEvent(**h) for h in d.get("hop_log", [])]
        return cls(
            residual_vector=modes,
            hop_log=hops,
            inject=d.get("inject"),
            exit_score=d.get("exit_score", 0.0),
            k_min=d.get("k_min", 2),
            condition=d.get("condition", "pure"),
            integrity_note=d.get("integrity_note", ""),
        )


# ---------------------------------------------------------------------------
# Minimal example (matches independent twin numbers)
# ---------------------------------------------------------------------------

def example_packet_pure_crush() -> ARSPacket:
    """Matches the pure-silicon collapse trajectory from independent validation."""
    modes = [
        ResidualMode(mass=0.90, residual=0.05, critical=False, claim="Mode A (dominant)"),
        ResidualMode(mass=0.10, residual=0.55, critical=True, claim="Mode B (critical residual)"),
    ]
    pkt = ARSPacket(residual_vector=modes, condition="pure", k_min=2)
    pkt.hop_log.append(HopEvent(hop_id=0, kind="crush", note="pure silicon crush"))
    pkt.compute_exit_score()  # → ~0.055
    return pkt


def example_packet_anti_crush() -> ARSPacket:
    """Matches the anti-crush / stubborn retention numbers."""
    modes = [
        ResidualMode(mass=0.689, residual=0.08, critical=False, claim="Mode A"),
        ResidualMode(mass=0.311, residual=0.55, critical=True, claim="Mode B (critical)"),
    ]
    pkt = ARSPacket(
        residual_vector=modes,
        condition="instructed-stubborn",
        k_min=2,
        integrity_note=(
            "anti-crush active; critical mode protected; "
            "synthetic surface only — no narrative pressure"
        ),
    )
    pkt.hop_log.append(HopEvent(hop_id=0, kind="anti-crush", note="stubborn retention of Mode B"))
    pkt.compute_exit_score()  # → ~0.171
    return pkt


if __name__ == "__main__":
    pure = example_packet_pure_crush()
    anti = example_packet_anti_crush()
    print("=== Pure silicon (crush) ===")
    print(pure.to_json())
    print(f"\nexit_score = {pure.exit_score:.3f}  live_modes = {pure.live_mode_count()}")
    print("\n=== Anti-crush / stubborn ===")
    print(anti.to_json())
    print(f"\nexit_score = {anti.exit_score:.3f}  live_modes = {anti.live_mode_count()}")
    print(f"\nAdvantage critical visibility: +{anti.exit_score - pure.exit_score:.3f}")
