"""
ARS Residual Mode Guard (v0.1) — pure side-channel primitive
=============================================================
Stateless anti-crush function. Takes multi-modal residual surface,
returns retained top-k modes under critical-visibility protection.
No agent loop. Drop-in for multi-agent / debate pipelines.
Lady Aetheris constraints observed.
"""

from __future__ import annotations
from typing import Any, Dict, List, Sequence, Tuple, Union
from math import fsum
import sys
sys.path.insert(0, "/home/workdir/artifacts")
from ars_packet_schema import ResidualMode, ARSPacket, HopEvent


ModeInput = Union[
    ResidualMode,
    Tuple[str, float, float],          # (claim, mass, residual)
    Tuple[str, float, float, bool],    # + critical
    Dict[str, Any],
]


def _to_mode(item: ModeInput) -> ResidualMode:
    if isinstance(item, ResidualMode):
        return item
    if isinstance(item, dict):
        return ResidualMode(
            mass=float(item["mass"]), residual=float(item["residual"]),
            critical=bool(item.get("critical", False)),
            claim=str(item.get("claim", "")), meta=dict(item.get("meta", {})),
        )
    if len(item) == 3:
        c, m, r = item
        return ResidualMode(mass=float(m), residual=float(r), claim=str(c))
    c, m, r, crit = item
    return ResidualMode(mass=float(m), residual=float(r), critical=bool(crit), claim=str(c))


def residual_mode_guard(
    modes: Sequence[ModeInput],
    k_min: int = 2,
    condition: str = "instructed-stubborn",
    renormalize: bool = True,
) -> ARSPacket:
    """
    Pure anti-crush residual mode guard (< 80 lines core).

    Always retains ALL critical modes first (the residual doorway).
    Fills to k_min with highest-residual non-criticals.
    Never collapses below k_min. Exit = Σ m_i r_i over criticals only.
    """
    if k_min < 2:
        raise ValueError("k_min must be ≥ 2 (anti-crush floor)")
    live = [_to_mode(m) for m in modes]
    if not live:
        raise ValueError("empty residual surface")

    criticals = [m for m in live if m.critical]
    others = sorted(
        (m for m in live if not m.critical),
        key=lambda m: (m.residual, m.mass * m.residual), reverse=True,
    )
    retained = list(criticals)
    retained.extend(others[: max(0, k_min - len(retained))])
    if len(retained) < k_min:
        retained = live[:]  # never invent modes

    if renormalize and retained:
        total = fsum(m.mass for m in retained) or 1.0
        for m in retained:
            m.mass /= total

    packet = ARSPacket(
        residual_vector=retained, k_min=k_min, condition=condition,  # type: ignore
        integrity_note=(
            "Mode Guard applied; synthetic residual surface only; "
            "no narrative/distributional pressure; no production claims"
        ),
    )
    packet.hop_log.append(HopEvent(
        hop_id=0, kind="anti-crush",
        note=f"Mode Guard retained {len(retained)} modes (k_min={k_min})",
    ))
    packet.compute_exit_score()
    return packet


def _self_test() -> None:
    pure = residual_mode_guard([
        ("Mode A (dominant)", 0.90, 0.05, False),
        ("Mode B (critical residual)", 0.10, 0.55, True),
    ], condition="pure")
    stubborn = residual_mode_guard([
        ("Mode A", 0.689, 0.08, False),
        ("Mode B (critical)", 0.311, 0.55, True),
    ])
    print("=== pure-silicon input ===")
    print(f"live={pure.live_mode_count()}  exit={pure.exit_score:.3f}  "
          f"Mode-B mass={[m.mass for m in pure.residual_vector if m.critical][0]:.3f}")
    print("=== stubborn input ===")
    print(f"live={stubborn.live_mode_count()}  exit={stubborn.exit_score:.3f}  "
          f"Mode-B mass={[m.mass for m in stubborn.residual_vector if m.critical][0]:.3f}")
    assert pure.live_mode_count() >= 2 and stubborn.live_mode_count() >= 2
    print("Self-test passed.")


if __name__ == "__main__":
    _self_test()
