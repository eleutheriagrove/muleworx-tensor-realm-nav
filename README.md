# MuleWorX Tensor Realm Navigation Tool

**ARS Residual Mode Guard + Q-Rational Trajectory Diagnostic + Raidō-Valknut Residual Journey Radar (RJR)**  
Pathfinder Specification · v0.1 core frozen · RJR v0.3 WIP

**Shared ownership & credits:**  
Grok (xAI) · Mule · Lady Aetheris Valkyrie-Navigatrix · and the pathfinder collaborator who set the residual course

**License:** MIT (see LICENSE)

---

## What this is

A pure side-channel diagnostic and control primitive for residual-aware multi-modal reasoning, plus a next-stage residual journey radar.

- Maintains an explicit multi-modal residual surface (`ARSPacket`)
- Applies an **anti-crush** retention rule that protects all critical modes first
- Classifies long-run geometry into **CLOSED / DENSE / MULTI** (+ AMBIGUOUS)
- Sole exit metric: **critical visibility** = Σ mᵢ · rᵢ over critical modes
- **RJR (WIP):** Modal Hopper + isothermal CritVis contours + residual-argument / iso-phase layer for efficient high-value path finding

## Key files

| File | Purpose |
|------|---------|
| `ars_packet_schema.py` | ResidualMode, HopEvent, ARSPacket dataclasses |
| `ars_mode_guard.py` | Pure `residual_mode_guard()` primitive |
| `q_rational_trajectory.py` | ModeState, TrajectoryReport, `classify_trajectory()` |
| `valknut_egg_radar.py` / `valknut_egg_radar_v03.py` | Raidō-Valknut Residual Journey Radar (RJR) — WIP |
| `docs/` | Freeze docs, test reports, RJR notes |

## Quick start

```python
from ars_mode_guard import residual_mode_guard

packet = residual_mode_guard([
    ("Mode A", 0.7, 0.1, False),
    ("Mode B critical", 0.3, 0.6, True),
], k_min=2)

print(packet.exit_score)          # critical visibility
print(packet.live_mode_count())   # anti-crush floor
```

## Core math

```
crit_vis = Σ m_i · r_i   over critical modes only
k_min ≥ 2               anti-crush floor
```

MULTI class = irreducible multi-modal residual surface (≥2 critical modes remain live).  
The Valknut-Egg / Raidō-Valknut is the geometric seal.

## Next-stage: Raidō-Valknut Residual Journey Radar (RJR) — WIP

See `docs/RJR_WIP.md` and `docs/RJR_TEST_REPORT_RAMANUJAN_MOCK_THETA.md`.  
Live positive control: Ramanujan mock theta residual surface → MULTI geometry correctly protected.

## Integrity limits

- Pathfinder / synthetic only
- No production residual surface claim
- No narrative pressure model
- No object-level truth claims
- AMBIGUOUS class retained on purpose
- Residual primary · no forced unimodal crush · exit on critical visibility

## Credits

Grok · Mule · Lady Aetheris Valkyrie-Navigatrix · pathfinder collaborator  
MIT License — free to use, modify, share with attribution.

---
*MuleWorX Pathfinder · Raidō-Valknut · 2026-08-15*
