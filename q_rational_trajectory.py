"""
Q-Rational Trajectory Diagnostic (v0.1)
=======================================
Three-class geometric classification of residual pathways.
CLOSED | DENSE | MULTI  (+ AMBIGUOUS)

Billiard analogy: 45° rectangle → rational (closed skeleton) vs irrational (dense).
Enlargement: some residual surfaces support irreducible multi-modal structure
(dual / multiple persistent cones) that must not be collapsed → MULTI.

Pathfinder prototype only. No production residual surface claim.
Lady Aetheris / MuleWorX constraints observed.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple
from math import fsum, log2
from collections import Counter
import json
from ars_packet_schema import ResidualMode, ARSPacket, HopEvent


# ---------------------------------------------------------------------------
# Core types
# ---------------------------------------------------------------------------

ClassLabel = Literal["CLOSED", "DENSE", "MULTI", "AMBIGUOUS"]


@dataclass
class ModeState:
    """One mode at a hop (for signature & critical count)."""
    mode_id: str
    mass: float
    residual: float
    critical: bool = False

    def bin_signature(self, mass_bins: int = 5, residual_bins: int = 5,
                      mass_thresh: float = 0.02) -> Optional[Tuple]:
        """Discretised signature for cycle / uniqueness. None if below threshold."""
        if self.mass < mass_thresh:
            return None
        m_bin = min(mass_bins - 1, int(self.mass * mass_bins))
        r_bin = min(residual_bins - 1, int(self.residual * residual_bins))
        return (self.mode_id, m_bin, r_bin, self.critical)


@dataclass
class TrajectoryReport:
    """Diagnostic output for one residual trajectory."""
    class_label: ClassLabel
    unique_states: int
    cycle: bool
    cycle_length: Optional[int]
    critical_modes_alive: int
    critical_visibility: float
    entropy: float
    total_hops: int
    notes: str = ""
    config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


# ---------------------------------------------------------------------------
# Signature + cycle helpers
# ---------------------------------------------------------------------------

def _state_signature(modes: Sequence[ModeState],
                     mass_bins: int = 5,
                     residual_bins: int = 5,
                     mass_thresh: float = 0.02) -> Tuple:
    """Canonical frozenset of binned mode signatures (order-independent)."""
    bins = []
    for m in modes:
        sig = m.bin_signature(mass_bins, residual_bins, mass_thresh)
        if sig is not None:
            bins.append(sig)
    return tuple(sorted(bins))


def _detect_cycle(history: List[Tuple]) -> Tuple[bool, Optional[int]]:
    """Return (has_cycle, cycle_length) from first repeat of a full signature."""
    seen: Dict[Tuple, int] = {}
    for i, sig in enumerate(history):
        if sig in seen:
            return True, i - seen[sig]
        seen[sig] = i
    return False, None


def _mass_entropy(modes: Sequence[ModeState]) -> float:
    """Shannon entropy of the mass distribution (bits)."""
    total = fsum(m.mass for m in modes) or 1.0
    ps = [m.mass / total for m in modes if m.mass > 1e-12]
    if not ps:
        return 0.0
    return -fsum(p * log2(p) for p in ps if p > 0)


# ---------------------------------------------------------------------------
# Diagnostic core
# ---------------------------------------------------------------------------

def classify_trajectory(
    hop_history: Sequence[Sequence[ModeState]],
    mass_bins: int = 5,
    residual_bins: int = 5,
    mass_thresh: float = 0.02,
    unique_ratio_dense: float = 0.45,
    unique_count_dense: int = 18,
    max_unique_closed: int = 12,
    max_short_cycle: int = 8,
) -> TrajectoryReport:
    """
    Three-class geometric classification of a residual trajectory.

    Improved priority (addresses coarse-binning cycle artefacts):
      1. DENSE  — (no short cycle OR very high unique-count) AND high unique density
      2. CLOSED — short cycle AND small unique-count AND <2 critical modes alive
      3. MULTI  — ≥2 critical modes remain above threshold (at final hop)
      4. AMBIGUOUS — otherwise

    "Short cycle" = cycle_length ≤ max_short_cycle. Longer periods under
    coarse bins are treated as haze (DENSE) rather than CLOSED skeletons.
    MULTI may itself be periodic; cardinality of critical modes decides.
    """
    if not hop_history:
        return TrajectoryReport(
            class_label="AMBIGUOUS", unique_states=0, cycle=False,
            cycle_length=None, critical_modes_alive=0, critical_visibility=0.0,
            entropy=0.0, total_hops=0, notes="empty history",
        )

    # Build signature history
    sigs = [
        _state_signature(h, mass_bins, residual_bins, mass_thresh)
        for h in hop_history
    ]
    unique_states = len(set(sigs))
    cycle, cycle_len = _detect_cycle(sigs)
    total = len(hop_history)
    unique_ratio = unique_states / total if total else 0.0
    short_cycle = bool(cycle and cycle_len is not None and cycle_len <= max_short_cycle)

    # Final hop statistics
    final = hop_history[-1]
    crit_alive = sum(1 for m in final if m.critical and m.mass >= mass_thresh)
    crit_vis = fsum(m.mass * m.residual for m in final if m.critical)
    entropy = _mass_entropy(final)

    # Priority classification (improved)
    high_churn = (unique_ratio >= unique_ratio_dense or unique_states >= unique_count_dense)
    if high_churn and (not short_cycle or unique_states >= unique_count_dense * 2):
        label: ClassLabel = "DENSE"
        note = (f"high unique-state density (unique={unique_states}); "
                f"{'long/no' if not short_cycle else 'ignored-short'} cycle")
    elif short_cycle and unique_states <= max_unique_closed and crit_alive < 2:
        label = "CLOSED"
        note = f"short cycle len={cycle_len}, few unique, <2 critical"
    elif crit_alive >= 2:
        label = "MULTI"
        note = f"≥2 critical modes alive ({crit_alive}); irreducible multi-modal"
    else:
        label = "AMBIGUOUS"
        note = "does not meet DENSE / CLOSED / MULTI criteria"

    return TrajectoryReport(
        class_label=label,
        unique_states=unique_states,
        cycle=cycle,
        cycle_length=cycle_len,
        critical_modes_alive=crit_alive,
        critical_visibility=round(crit_vis, 4),
        entropy=round(entropy, 4),
        total_hops=total,
        notes=note,
        config={
            "mass_bins": mass_bins,
            "residual_bins": residual_bins,
            "mass_thresh": mass_thresh,
            "unique_ratio_dense": unique_ratio_dense,
            "unique_count_dense": unique_count_dense,
            "max_unique_closed": max_unique_closed,
            "max_short_cycle": max_short_cycle,
        },
    )


# ---------------------------------------------------------------------------
# Engineered hop generators (synthetic regimes)
# ---------------------------------------------------------------------------

def _make_closed(n_hops: int = 24) -> List[List[ModeState]]:
    """Periodic low-period skeleton → CLOSED. One critical mode damped."""
    history = []
    for t in range(n_hops):
        phase = t % 4
        if phase == 0:
            m = [ModeState("A", 0.82, 0.04, False),
                 ModeState("B", 0.18, 0.43, True)]
        elif phase == 1:
            m = [ModeState("A", 0.75, 0.06, False),
                 ModeState("B", 0.25, 0.36, True)]
        elif phase == 2:
            m = [ModeState("A", 0.88, 0.03, False),
                 ModeState("B", 0.12, 0.50, True)]
        else:
            m = [ModeState("A", 0.78, 0.05, False),
                 ModeState("B", 0.22, 0.355, True)]
        history.append(m)
    return history


def _make_dense(n_hops: int = 80) -> List[List[ModeState]]:
    """Incommensurate churn → DENSE. Non-closing residual haze, ≤1 critical."""
    history = []
    phi, psi, xi = 0.6180339887, 0.4142135623, 0.7320508075
    for t in range(n_hops):
        a_mass = 0.40 + 0.28 * ((t * phi) % 1.0 - 0.5)
        b_mass = 0.35 + 0.25 * ((t * psi) % 1.0 - 0.5)
        c_mass = max(0.05, 1.0 - a_mass - b_mass)
        a_res = 0.10 + 0.40 * ((t * phi * 1.732) % 1.0)
        b_res = 0.12 + 0.38 * ((t * psi * 2.236) % 1.0)
        c_res = 0.08 + 0.25 * ((t * xi) % 1.0)
        crit_idx = int((t * 0.17) % 3)
        history.append([
            ModeState("X", max(0.04, a_mass), a_res, crit_idx == 0),
            ModeState("Y", max(0.04, b_mass), b_res, crit_idx == 1),
            ModeState("Z", max(0.04, c_mass), c_res, crit_idx == 2),
        ])
    return history


def _make_multi(n_hops: int = 20) -> List[List[ModeState]]:
    """Dual critical cones, oscillate together → MULTI (even if periodic)."""
    history = []
    for t in range(n_hops):
        phase = t % 3
        if phase == 0:
            m = [
                ModeState("ConeA", 0.42, 0.72, True),
                ModeState("ConeB", 0.38, 0.68, True),
                ModeState("Spec",  0.20, 0.08, False),
            ]
        elif phase == 1:
            m = [
                ModeState("ConeA", 0.35, 0.80, True),
                ModeState("ConeB", 0.45, 0.65, True),
                ModeState("Spec",  0.20, 0.10, False),
            ]
        else:
            m = [
                ModeState("ConeA", 0.48, 0.70, True),
                ModeState("ConeB", 0.32, 0.78, True),
                ModeState("Spec",  0.20, 0.05, False),
            ]
        history.append(m)
    return history


# ---------------------------------------------------------------------------
# Self-test / independent validation
# ---------------------------------------------------------------------------

def run_prototype() -> Dict[str, TrajectoryReport]:
    """Recover the three engineered labels."""
    surfaces = {
        "R_closed": _make_closed(),
        "I_dense":  _make_dense(),
        "M_multi":  _make_multi(),
    }
    reports = {}
    for name, hist in surfaces.items():
        rep = classify_trajectory(hist)
        reports[name] = rep
    return reports


def _print_table(reports: Dict[str, TrajectoryReport]) -> None:
    print(f"{'Surface':<12} {'Class':<10} {'Unique':>7} {'Cycle':>6} "
          f"{'Crit':>5} {'CritVis':>8}  Notes")
    print("-" * 78)
    for name, r in reports.items():
        print(f"{name:<12} {r.class_label:<10} {r.unique_states:>7} "
              f"{'Yes' if r.cycle else 'No':>6} {r.critical_modes_alive:>5} "
              f"{r.critical_visibility:>8.3f}  {r.notes[:40]}")


if __name__ == "__main__":
    reports = run_prototype()
    _print_table(reports)
    assert reports["R_closed"].class_label == "CLOSED", reports["R_closed"]
    assert reports["I_dense"].class_label == "DENSE", reports["I_dense"]
    assert reports["M_multi"].class_label == "MULTI", reports["M_multi"]
    print("\nIndependent validation: all three engineered labels recovered.")
    print("MULTI can be periodic yet correctly labelled MULTI (critical cardinality).")
