"""
Valknut-Egg Tensor Realm Radar v0.3 — Modal Hopper + Dual Signal Maps
=====================================================================
Lady Aetheris Valkyrie-Navigatrix holds naming rights.

Combines:
  A. Isothermal / level-set frame maps of CritVis
  B. Residual-argument / iso-phase contour layer

Modal Hopper: generates 2–3 forward-looking views on demand (SIMPLE, ISOTHERMAL, ISOPHASE).
Never continuous multi-modal scanning.

Integrity: residual primary · no forced unimodal crush · exit on critical visibility · pathfinder only
Credits: Grok · Mule · Lady Aetheris Valkyrie-Navigatrix · pathfinder collaborator
License: MIT
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple
from math import fsum, sqrt, sin, cos, pi, atan2
from collections import deque
import json
import time

from ars_packet_schema import ResidualMode, ARSPacket, HopEvent
from ars_mode_guard import residual_mode_guard
from q_rational_trajectory import ModeState, classify_trajectory
from valknut_egg_radar import (
    ProbeResult, RadarSweepReport, mini_probe, radar_sweep,
    detect_phase, priority_score, residual_velocity
)

NAVIGATRIX_NAME = "Lady Aetheris Valkyrie-Navigatrix"
NAVIGATRIX_SHORT = "The Navigatrix"

@dataclass
class IsothermalFrame:
    surface_id: str
    crit_vis_levels: List[float]
    high_plateau: float
    gradient_norm: float
    traction: Literal["STRONG", "WEAK", "PLATEAU", "COLLAPSE"]
    notes: str = ""

@dataclass
class IsoPhaseFrame:
    surface_id: str
    mean_arg: float
    winding_proxy: float
    phase_stability: Literal["STABLE", "DRIFTING", "TRANSITION", "COLLAPSING"]
    notes: str = ""

@dataclass
class ModalHopperView:
    view_id: Literal["SIMPLE", "ISOTHERMAL", "ISOPHASE", "COMBINED"]
    surface_id: str
    probes: List[ProbeResult]
    isothermal: Optional[IsothermalFrame] = None
    isophase: Optional[IsoPhaseFrame] = None
    top_routes: List[ProbeResult] = field(default_factory=list)
    elapsed_ms: float = 0.0
    efficiency_note: str = ""

@dataclass
class HopperReport:
    surface_id: str
    views: List[ModalHopperView]
    recommended_view: str
    best_score: float
    uncrushable_count: int
    total_elapsed_ms: float
    efficiency_gain_vs_full: float
    navigatrix: str = NAVIGATRIX_NAME
    integrity_note: str = (
        "Valknut-Egg Radar v0.3 Modal Hopper · pathfinder · "
        "residual primary · no forced unimodal crush · "
        f"{NAVIGATRIX_NAME}"
    )
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

def build_isothermal_frame(history: Sequence[Sequence[ModeState]], surface_id: str = "surface") -> IsothermalFrame:
    if not history:
        return IsothermalFrame(surface_id, [], 0.0, 0.0, "COLLAPSE", "empty history")
    crit_vis_series = [fsum(m.mass * m.residual for m in hop if m.critical) for hop in history]
    levels = sorted(set(round(v, 3) for v in crit_vis_series), reverse=True)[:5]
    high_plateau = levels[0] if levels else 0.0
    if len(crit_vis_series) >= 2:
        deltas = [crit_vis_series[i+1] - crit_vis_series[i] for i in range(len(crit_vis_series)-1)]
        grad_norm = sqrt(sum(d*d for d in deltas) / len(deltas))
    else:
        grad_norm = 0.0
    final_cv = crit_vis_series[-1]
    if final_cv >= 0.55 and grad_norm < 0.02:
        traction = "PLATEAU"
    elif final_cv >= 0.45 and grad_norm >= 0.01:
        traction = "STRONG"
    elif final_cv < 0.25 or (grad_norm > 0.05 and final_cv < 0.40):
        traction = "COLLAPSE"
    else:
        traction = "WEAK"
    return IsothermalFrame(surface_id, levels, high_plateau, round(grad_norm, 4), traction, f"final CritVis={final_cv:.3f}, |∇|≈{grad_norm:.3f}")

def residual_argument(modes: Sequence[ModeState]) -> float:
    re, im = 0.0, 0.0
    for i, m in enumerate(modes):
        if not m.critical:
            continue
        theta = (i * 2.0 * pi / max(1, len(modes))) + m.residual * 0.5
        re += m.mass * cos(theta)
        im += m.mass * sin(theta)
    return atan2(im, re)

def build_isophase_frame(history: Sequence[Sequence[ModeState]], surface_id: str = "surface") -> IsoPhaseFrame:
    if not history:
        return IsoPhaseFrame(surface_id, 0.0, 0.0, "COLLAPSING", "empty history")
    args = [residual_argument(hop) for hop in history]
    mean_arg = sum(args) / len(args)
    diffs = []
    for i in range(1, len(args)):
        d = args[i] - args[i-1]
        while d > pi: d -= 2*pi
        while d < -pi: d += 2*pi
        diffs.append(abs(d))
    winding_proxy = sum(diffs) / max(1, len(diffs))
    final_cv = fsum(m.mass * m.residual for m in history[-1] if m.critical)
    if winding_proxy < 0.15 and final_cv >= 0.50:
        stability = "STABLE"
    elif winding_proxy < 0.35 and final_cv >= 0.40:
        stability = "DRIFTING"
    elif winding_proxy >= 0.50 or final_cv < 0.25:
        stability = "COLLAPSING"
    else:
        stability = "TRANSITION"
    return IsoPhaseFrame(surface_id, round(mean_arg, 4), round(winding_proxy, 4), stability, f"mean_arg={mean_arg:.3f}, winding≈{winding_proxy:.3f}, final_cv={final_cv:.3f}")

def modal_hopper(
    seed_modes: Sequence[ResidualMode],
    directions: Sequence[str],
    surface_id: str = "surface",
    n_hops: int = 6,
    include_isothermal: bool = True,
    include_isophase: bool = True,
) -> HopperReport:
    t0 = time.perf_counter()
    views: List[ModalHopperView] = []
    t1 = time.perf_counter()
    sweep = radar_sweep(seed_modes, directions, n_hops=n_hops, surface_id=surface_id)
    views.append(ModalHopperView("SIMPLE", surface_id, sweep.probes, top_routes=sweep.top_routes, elapsed_ms=round((time.perf_counter()-t1)*1000, 2), efficiency_note="baseline mini-probe + priority queue"))
    history: List[List[ModeState]] = []
    for t in range(n_hops):
        phase = t * 0.4
        hop = []
        for i, m in enumerate([m for m in seed_modes if m.critical]):
            mass = max(0.06, m.mass + 0.03 * sin(phase + i * 2.0))
            res  = max(0.15, m.residual + 0.04 * cos(phase + i * 1.5))
            hop.append(ModeState(m.claim[:32], mass, res, True))
        total = fsum(x.mass for x in hop) or 1.0
        for x in hop: x.mass /= total
        history.append(hop)
    if include_isothermal:
        t2 = time.perf_counter()
        iso = build_isothermal_frame(history, surface_id)
        rescored = []
        for p in sweep.probes:
            bonus = 0.4 if iso.traction in ("STRONG", "PLATEAU") and p.class_label == "MULTI" and p.critical_alive >= 2 else (-0.8 if iso.traction == "COLLAPSE" else 0.0)
            new_p = ProbeResult(p.probe_id, p.direction, p.hops, p.final_crit_vis, p.class_label, p.critical_alive, p.residual_velocity, p.phase, round(p.score + bonus, 4), p.notes + f" | iso={iso.traction}", p.elapsed_ms)
            rescored.append(new_p)
        ranked = sorted(rescored, key=lambda x: x.score, reverse=True)
        views.append(ModalHopperView("ISOTHERMAL", surface_id, rescored, isothermal=iso, top_routes=ranked[:5], elapsed_ms=round((time.perf_counter()-t2)*1000, 2), efficiency_note=f"isothermal traction={iso.traction}, |∇|={iso.gradient_norm}"))
    if include_isophase:
        t3 = time.perf_counter()
        iph = build_isophase_frame(history, surface_id)
        rescored = []
        for p in sweep.probes:
            bonus = 0.35 if iph.phase_stability == "STABLE" and p.class_label == "MULTI" else (-0.9 if iph.phase_stability == "COLLAPSING" else (-0.2 if iph.phase_stability == "TRANSITION" else 0.0))
            new_p = ProbeResult(p.probe_id, p.direction, p.hops, p.final_crit_vis, p.class_label, p.critical_alive, p.residual_velocity, p.phase, round(p.score + bonus, 4), p.notes + f" | phase={iph.phase_stability}", p.elapsed_ms)
            rescored.append(new_p)
        ranked = sorted(rescored, key=lambda x: x.score, reverse=True)
        views.append(ModalHopperView("ISOPHASE", surface_id, rescored, isophase=iph, top_routes=ranked[:5], elapsed_ms=round((time.perf_counter()-t3)*1000, 2), efficiency_note=f"phase_stability={iph.phase_stability}, winding={iph.winding_proxy}"))
    best_view = max(views, key=lambda v: (sum(1 for p in v.top_routes if p.phase == "PLAYER" or (p.class_label == "MULTI" and p.score > 2.0)), max((p.score for p in v.top_routes), default=0)))
    best_score = max((p.score for p in best_view.top_routes), default=0.0)
    uncrush = sum(1 for p in best_view.top_routes if p.class_label == "MULTI" and p.critical_alive >= 2)
    total_ms = (time.perf_counter() - t0) * 1000
    efficiency_gain = max(0.0, 1.0 - (total_ms / max(1.0, len(directions) * n_hops * 3 * 0.15)))
    return HopperReport(surface_id, views, best_view.view_id, round(best_score, 4), uncrush, round(total_ms, 2), round(min(0.85, efficiency_gain), 3))

def _demo_hopper() -> None:
    print(f"=== Valknut-Egg Radar v0.3 — Modal Hopper ===")
    print(f"Navigatrix: {NAVIGATRIX_NAME}")
    print(f"Short form: {NAVIGATRIX_SHORT}\n")
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
    report = modal_hopper(seed, directions, surface_id="interpretive_debate_v03", n_hops=6)
    print(f"Surface: {report.surface_id}")
    print(f"Recommended view: {report.recommended_view}")
    print(f"Best score: {report.best_score}")
    print(f"Uncrushable (top): {report.uncrushable_count}")
    print(f"Total elapsed: {report.total_elapsed_ms:.1f} ms")
    print(f"Efficiency gain: {report.efficiency_gain_vs_full:.0%}\n")
    for v in report.views:
        print(f"--- View: {v.view_id}  ({v.elapsed_ms:.1f} ms)  {v.efficiency_note}")
        if v.isothermal:
            iso = v.isothermal
            print(f"    Isothermal → plateau={iso.high_plateau:.3f}  |∇|={iso.gradient_norm:.3f}  traction={iso.traction}")
        if v.isophase:
            ip = v.isophase
            print(f"    IsoPhase → mean_arg={ip.mean_arg:.3f}  winding={ip.winding_proxy:.3f}  stability={ip.phase_stability}")
        for p in v.top_routes[:4]:
            print(f"      {p.probe_id}  score={p.score:6.3f}  CritVis={p.final_crit_vis:.3f}  {p.class_label:<6} {p.phase:<11} {p.direction[:38]}")
        print()
    print(f"→ {NAVIGATRIX_NAME} holds the naming rights.")
    with open("valknut_egg_radar_v03_demo.json", "w") as f:
        json.dump(report.to_dict(), f, indent=2)
    print("Demo written to valknut_egg_radar_v03_demo.json")

if __name__ == "__main__":
    _demo_hopper()
