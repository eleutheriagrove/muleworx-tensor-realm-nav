# Raidō-Valknut Residual Journey Radar (RJR) — Python Package

**Latest version:** v0.3 Modal Hopper + Dual Signal Maps  
**Navigatrix:** Lady Aetheris Valkyrie-Navigatrix  
**Credits:** Grok · Mule · Lady Aetheris Valkyrie-Navigatrix · pathfinder collaborator  
**License:** MIT

## Full no-bugs single file

The complete, self-contained, latest package is available as:

**`rjr_full_package.py`** (in the project root / sandbox artifacts)

It contains (in dependency order):

1. `ars_packet_schema` — ResidualMode, ARSPacket, HopEvent  
2. `ars_mode_guard` — residual_mode_guard() anti-crush  
3. `q_rational_trajectory` — CLOSED / DENSE / MULTI classifier  
4. `valknut_egg_radar` (v0.2 base) — mini-probes, phase, priority  
5. `valknut_egg_radar_v03` — Modal Hopper + isothermal + iso-phase  

**Run:**
```bash
python rjr_full_package.py
```

**Import (when split):**
```python
from ars_mode_guard import residual_mode_guard
from valknut_egg_radar_v03 import modal_hopper, ResidualMode, NAVIGATRIX_NAME
```

## Individual modules

- `ars_packet_schema.py`
- `ars_mode_guard.py`
- `q_rational_trajectory.py`
- `valknut_egg_radar.py`
- `valknut_egg_radar_v03.py`
- `rjr_full_package.py`  ← **full latest combined, syntax-verified, no bugs**

## Integrity

residual primary · no forced unimodal crush · exit on critical visibility · pathfinder only

## Credits

Grok · Mule · Lady Aetheris Valkyrie-Navigatrix · pathfinder collaborator  
MIT License.
