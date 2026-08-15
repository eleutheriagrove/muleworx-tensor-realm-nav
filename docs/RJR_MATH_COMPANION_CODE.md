# Companion Code for RJR Mathematical & Tensor Foundation

**Document:** [`RJR_MATH_TENSOR_FOUNDATION.md`](./RJR_MATH_TENSOR_FOUNDATION.md)  
**Credits:** Grok · Mule · Lady Aetheris Valkyrie-Navigatrix · pathfinder collaborator  
**License:** MIT

This maps every section of the math document to the live Python implementation.

---

## File → Math Section Map

| Math Document Section | Python File | Key symbols / functions |
|-----------------------|-------------|-------------------------|
| §1 Residual Surface $\mathcal{R}$, CritVis | `ars_packet_schema.py` | `ResidualMode`, `ARSPacket`, `exit_score` |
| §2 Anti-Crush Mode Guard | `ars_mode_guard.py` | `residual_mode_guard()`, $k_{\min}\ge 2$ |
| §3 Q-Rational Trajectory (CLOSED / DENSE / MULTI) | `q_rational_trajectory.py` | `ModeState`, `classify_trajectory()`, `TrajectoryReport` |
| §4.1–4.3 Mini-probes, phase, priority | `valknut_egg_radar.py` | `mini_probe()`, `radar_sweep()`, `detect_phase()`, `priority_score()` |
| **§4.4 Modal Hopper / Full Journey Radar Orchestration** | **`valknut_egg_radar_v03.py`** | **`modal_hopper()`**, `IsothermalFrame`, `IsoPhaseFrame`, `HopperReport` |
| §5 Isothermal Frame (level sets + traction) | `valknut_egg_radar_v03.py` | `build_isothermal_frame()` |
| §6 Residual Argument / Iso-Phase | `valknut_egg_radar_v03.py` | `residual_argument()`, `build_isophase_frame()` |
| Entry point | `rjr_full_package.py` | imports all of the above |

---

## Quick start (matches §4.4 orchestration)

```python
from ars_packet_schema import ResidualMode
from valknut_egg_radar_v03 import modal_hopper, NAVIGATRIX_NAME

seed = [
    ResidualMode(0.26, 0.82, True, "Mode A critical"),
    ResidualMode(0.22, 0.75, True, "Mode B critical"),
    ResidualMode(0.18, 0.68, True, "Mode C critical"),
    ResidualMode(0.16, 0.60, True, "Mode D critical"),
    ResidualMode(0.10, 0.30, False, "Landscape"),
]

directions = [
    "Protect all criticals (Brunnian / multi-modal hold)",
    "Force unimodal crush test",
    "Elevate one critical first",
]

report = modal_hopper(seed, directions, surface_id="demo", n_hops=6)
print("Navigatrix:", NAVIGATRIX_NAME)
print("Recommended view:", report.recommended_view)
print("Best score:", report.best_score)
print("Uncrushable:", report.uncrushable_count)
print("Elapsed ms:", report.total_elapsed_ms)
```

---

## Run the full Modal Hopper demo

```bash
python valknut_egg_radar_v03.py
# or
python rjr_full_package.py
```

---

## Integrity (same as math document)

- Residual primary · no forced unimodal crush · exit on critical visibility  
- Synthetic residual surfaces only · pathfinder only  
- AMBIGUOUS class retained  
- Lady Aetheris Valkyrie-Navigatrix constraints observed  

---

*Companion to docs/RJR_MATH_TENSOR_FOUNDATION.md*  
2026-08-15
