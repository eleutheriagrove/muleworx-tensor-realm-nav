"""
Raidō-Valknut Residual Journey Radar (RJR) — Full Package Entry
==============================================================
v0.3 Modal Hopper + Dual Signal Maps

Companion to: docs/RJR_MATH_TENSOR_FOUNDATION.md
             docs/RJR_MATH_COMPANION_CODE.md

Navigatrix: Lady Aetheris Valkyrie-Navigatrix
Credits: Grok · Mule · Lady Aetheris Valkyrie-Navigatrix · pathfinder collaborator
License: MIT

Integrity: residual primary · no forced unimodal crush · exit on critical visibility
           · hard integrity limits · pathfinder only · no production residual surface claim
"""

from __future__ import annotations

from ars_packet_schema import ResidualMode, ARSPacket, HopEvent
from ars_mode_guard import residual_mode_guard
from q_rational_trajectory import ModeState, classify_trajectory, TrajectoryReport
from valknut_egg_radar import (
    ProbeResult, RadarSweepReport, mini_probe, radar_sweep,
    detect_phase, priority_score, residual_velocity,
)
from valknut_egg_radar_v03 import (
    modal_hopper, HopperReport, ModalHopperView,
    IsothermalFrame, IsoPhaseFrame,
    NAVIGATRIX_NAME, NAVIGATRIX_SHORT,
    build_isothermal_frame, build_isophase_frame,
)

__all__ = [
    "ResidualMode", "ARSPacket", "HopEvent",
    "residual_mode_guard",
    "ModeState", "classify_trajectory", "TrajectoryReport",
    "ProbeResult", "RadarSweepReport", "mini_probe", "radar_sweep",
    "detect_phase", "priority_score", "residual_velocity",
    "modal_hopper", "HopperReport", "ModalHopperView",
    "IsothermalFrame", "IsoPhaseFrame",
    "NAVIGATRIX_NAME", "NAVIGATRIX_SHORT",
    "build_isothermal_frame", "build_isophase_frame",
]

if __name__ == "__main__":
    print("Raidō-Valknut Residual Journey Radar (RJR)")
    print("Navigatrix:", NAVIGATRIX_NAME)
    print("Math foundation: docs/RJR_MATH_TENSOR_FOUNDATION.md")
    print("Running Modal Hopper demo...\n")
    from valknut_egg_radar_v03 import _demo_hopper
    _demo_hopper()
