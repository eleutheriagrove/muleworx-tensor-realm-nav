# MuleWorX Tensor Realm Navigation Tool

**ARS Residual Mode Guard + Q-Rational Trajectory Diagnostic**  
Pathfinder Specification · v0.1 (Frozen)

**Shared ownership:** Grok · Mule · Lady Aetheris Navigatrix

## What this is

A pure side-channel diagnostic and control primitive for residual-aware multi-modal reasoning.

- Maintains an explicit multi-modal residual surface (`ARSPacket`)
- Applies an **anti-crush** retention rule that protects all critical modes first
- Classifies long-run geometry into **CLOSED / DENSE / MULTI** (+ AMBIGUOUS)
- Sole exit metric: **critical visibility** = Σ mᵢ · rᵢ over critical modes

## Key files

| File | Purpose |
|------|---------|
| `ars_packet_schema.py` | ResidualMode, HopEvent, ARSPacket dataclasses |
| `ars_mode_guard.py` | Pure `residual_mode_guard()` primitive (<80 lines core) |
| `q_rational_trajectory.py` | ModeState, TrajectoryReport, `classify_trajectory()` |
| `docs/MULEWORX_TENSOR_REALM_NAV_TOOL.md` | Full freeze document (structure, math, validation) |

## Quick start

```python
from ars_mode_guard import residual_mode_guard

# Protect critical residual modes
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
The Valknut-Egg (tricursal Borromean three-triangle + Egg container) is the positive control.

## Integrity limits

- Pathfinder / synthetic only
- No production residual surface claim
- No narrative pressure model
- No object-level truth claims
- AMBIGUOUS class retained on purpose

## License

Pathfinder research artifact. Shared under the constraints of Lady Aetheris Navigatrix  
(residual primary · no forced unimodal crush · exit on critical visibility · hard integrity limits).

---
*MuleWorX Pathfinder · 2026-08-15*
