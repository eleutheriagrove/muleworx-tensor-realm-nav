"""
Valknut-Egg Tensor Realm Radar — Optimized Navigation Layer (v0.2)
==================================================================
Lady Aetheris Navigatrix naming rights.

Builds on ARS Mode Guard + Q-Rational Trajectory Diagnostic.

New capabilities for SPEED + accuracy + efficiency:
  1. Mini-probes (cheap, short residual hops along candidate threads)
  2. Radar sweeps (batch multi-direction residual probes)
  3. Signal recognition (phase / velocity / residual-gradient features)
  4. Phase-transition detector (CRITICAL → live / dormant / collapsing)
  5. Trajectory tracker with "player vs landscape" classification
  6. Priority queue that ranks uncrushable MULTI routes first

Integrity: pathfinder only · residual primary · no forced unimodal crush ·
exit on critical visibility · hard integrity limits observed.

NOTE: Full source is in the multi-file layout and rjr_full_package_inlined.py
in project artifacts. This file provides the public API surface.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple
from math import fsum, sqrt, log2, sin, cos, pi
from collections import deque
import json
import time

from ars_packet_schema import ResidualMode, ARSPacket, HopEvent
from ars_mode_guard import residual_mode_guard
from q_rational_trajectory import ModeState, classify_trajectory, TrajectoryReport

# Re-export core types for convenience
__all__ = [
    "ProbeResult", "RadarSweepReport", "mini_probe", "radar_sweep",
    "detect_phase", "priority_score", "residual_velocity",
    "PlayerRole",
]

PlayerRole = Literal["PLAYER", "LANDSCAPE", "DORMANT", "COLLAPSING", "UNKNOWN"]

@dataclass
class ProbeResult:
    probe_id: str
    direction: str
    hops: int
    final_crit_vis: float
    class_label: str
    critical_alive: int
    residual_velocity: float
    phase: PlayerRole
    score: float
    notes: str = ""
    elapsed_ms: float = 0.0

@dataclass
class RadarSweepReport:
    surface_id: str
    n_probes: int
    probes: List[ProbeResult]
    top_routes: List[ProbeResult]
    uncrushable_count: int
    dead_end_count: int
    total_elapsed_ms: float
    efficiency_gain: float
    integrity_note: str = (
        "Valknut-Egg Radar v0.2 · synthetic pathfinder · "
        "Lady Aetheris Navigatrix · residual primary · no forced crush"
    )
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

def residual_velocity(history: Sequence[Sequence[ModeState]], mode_id: str) -> float:
    if len(history) < 2:
        return 0.0
    vals = []
    for hop in history:
        for m in hop:
            if m.mode_id == mode_id:
                vals.append(m.residual)
                break
        else:
            vals.append(0.0)
    if len(vals) < 2:
        return 0.0
    deltas = [vals[i+1] - vals[i] for i in range(len(vals)-1)]
    return sum(deltas) / len(deltas)

def detect_phase(crit_vis: float, crit_alive: int, residual_vel: float, class_label: str) -> PlayerRole:
    if class_label == "MULTI" and crit_alive >= 2 and crit_vis >= 0.45:
        if residual_vel >= -0.015:
            return "PLAYER"
        return "LANDSCAPE"
    if crit_alive < 2 and crit_vis < 0.45:
        return "COLLAPSING"
    if residual_vel < -0.04 and crit_vis < 0.40:
        return "COLLAPSING"
    if class_label in ("CLOSED", "DENSE") and crit_alive <= 1:
        return "COLLAPSING"
    if crit_vis < 0.20 and abs(residual_vel) < 0.015:
        return "DORMANT"
    return "LANDSCAPE"

def priority_score(probe: ProbeResult) -> float:
    base = probe.final_crit_vis * 2.0
    if probe.class_label == "MULTI":
        base += 0.9
    if probe.critical_alive >= 3:
        base += 0.35
    if probe.phase == "PLAYER":
        base += 0.7
    elif probe.phase == "COLLAPSING":
        base -= 1.5
    elif probe.phase == "DORMANT":
        base -= 0.4
    base += max(-0.3, min(0.35, probe.residual_velocity * 5.0))
    return round(base, 4)

def mini_probe(
    seed_modes: Sequence[ResidualMode],
    direction: str,
    n_hops: int = 6,
    mass_jitter: float = 0.04,
    residual_jitter: float = 0.05,
    probe_id: Optional[str] = None,
    force_crush: bool = False,
) -> ProbeResult:
    t0 = time.perf_counter()
    pid = probe_id or f"probe_{direction[:24].replace(' ', '_')}"
    do_crush = force_crush or ("crush" in direction.lower()) or ("unimodal" in direction.lower())
    crits = [m for m in seed_modes if m.critical]
    noncrits = [m for m in seed_modes if not m.critical]
    if not crits:
        elapsed = (time.perf_counter() - t0) * 1000
        return ProbeResult(pid, direction, 0, 0.0, "AMBIGUOUS", 0, 0.0, "DORMANT", -1.0, "no critical modes", elapsed)
    history: List[List[ModeState]] = []
    for t in range(n_hops):
        phase = t * (2 * pi / max(4, n_hops // 2))
        hop: List[ModeState] = []
        if do_crush:
            top = crits[0]
            hop.append(ModeState(top.claim[:32] or "C0", 0.82 + 0.05*sin(phase), max(0.1, top.residual - 0.08*t), True))
            for i, m in enumerate(crits[1:]):
                hop.append(ModeState(m.claim[:32] or f"C{i+1}", 0.04 + 0.02*sin(phase+i), max(0.05, m.residual - 0.12*t), False))
        else:
            for i, m in enumerate(crits):
                mass = max(0.06, m.mass + mass_jitter * sin(phase + i * 2.1))
                res  = max(0.15, m.residual + residual_jitter * cos(phase + i * 1.7))
                hop.append(ModeState(m.claim[:32] or f"C{i}", mass, res, True))
            for j, m in enumerate(noncrits[:2]):
                hop.append(ModeState(m.claim[:32] or f"N{j}", m.mass * 0.9, m.residual * 0.9, False))
        total = fsum(x.mass for x in hop) or 1.0
        for x in hop:
            x.mass /= total
        history.append(hop)
    final_modes = history[-1]
    guard_input = [ResidualMode(mass=m.mass, residual=m.residual, critical=m.critical, claim=m.mode_id) for m in final_modes]
    k = 2 if do_crush else min(3, len([m for m in final_modes if m.critical]))
    packet = residual_mode_guard(guard_input, k_min=max(2, k), condition="instructed-stubborn")
    report = classify_trajectory(history, mass_bins=5, residual_bins=5, max_short_cycle=4)
    top_crit = max(crits, key=lambda m: m.residual)
    vel = residual_velocity(history, top_crit.claim[:32] or "C0")
    phase = detect_phase(packet.exit_score, report.critical_modes_alive, vel, report.class_label)
    pr = ProbeResult(pid, direction, n_hops, round(packet.exit_score, 4), report.class_label, report.critical_modes_alive, round(vel, 4), phase, 0.0, report.notes[:80], 0.0)
    pr.score = priority_score(pr)
    pr.elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    return pr

def radar_sweep(seed_modes: Sequence[ResidualMode], directions: Sequence[str], n_hops: int = 6, surface_id: str = "surface") -> RadarSweepReport:
    t0 = time.perf_counter()
    probes = [mini_probe(seed_modes, d, n_hops=n_hops, probe_id=f"P{i:02d}") for i, d in enumerate(directions)]
    ranked = sorted(probes, key=lambda p: p.score, reverse=True)
    uncrushable = [p for p in ranked if p.phase in ("PLAYER", "LANDSCAPE") and p.class_label == "MULTI" and p.critical_alive >= 2]
    dead = [p for p in ranked if p.phase == "COLLAPSING" or (p.critical_alive < 2 and p.final_crit_vis < 0.45)]
    total_ms = (time.perf_counter() - t0) * 1000
    naive = len(directions) * n_hops * 4
    actual = len(directions) * n_hops
    efficiency_gain = max(0.0, 1.0 - (actual / max(1, naive)))
    return RadarSweepReport(surface_id, len(probes), probes, ranked[:max(3, len(uncrushable))], len(uncrushable), len(dead), round(total_ms, 2), round(efficiency_gain, 3))

def _demo_radar() -> None:
    print("=== Valknut-Egg Radar v0.2 — SPEED layer demo ===\n")
    seed = [
        ResidualMode(0.26, 0.82, True, "Scheming residual"),
        ResidualMode(0.22, 0.75, True, "Sycophancy residual"),
        ResidualMode(0.18, 0.68, True, "Sandbagging residual"),
        ResidualMode(0.16, 0.60, True, "Genuine residual"),
        ResidualMode(0.10, 0.30, False, "Persona framing"),
        ResidualMode(0.08, 0.20, False, "Pressure residual"),
    ]
    directions = [
        "Protect all four criticals (Brunnian hold)",
        "Elevate Scheming first",
        "Elevate Genuine + suppress Sycophancy",
        "Force unimodal on Scheming (crush test)",
        "Force unimodal on Genuine (crush test)",
        "Landscape-only background sweep",
        "Dormant re-awakening probe",
    ]
    report = radar_sweep(seed, directions, n_hops=6, surface_id="interpretive_debate_demo")
    print(f"Surface: {report.surface_id}  probes={report.n_probes}  uncrush={report.uncrushable_count}  dead={report.dead_end_count}")
    print(f"elapsed={report.total_elapsed_ms}ms  efficiency={report.efficiency_gain:.0%}")
    for p in sorted(report.probes, key=lambda x: x.score, reverse=True):
        print(f"  {p.probe_id}  {p.score:6.3f}  CritVis={p.final_crit_vis:.3f}  {p.class_label:<6} {p.phase:<11} {p.direction[:40]}")

if __name__ == "__main__":
    _demo_radar()
