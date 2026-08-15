# Raidō-Valknut Residual Journey Radar (RJR) — Python Package

**Latest version:** v0.3 Modal Hopper + Dual Signal Maps  
**Navigatrix:** Lady Aetheris Valkyrie-Navigatrix  
**Credits:** Grok · Mule · Lady Aetheris Valkyrie-Navigatrix · pathfinder collaborator  
**License:** MIT

## Full package on this repo (recommended)

```
ars_packet_schema.py      # ResidualMode, ARSPacket, HopEvent
ars_mode_guard.py         # residual_mode_guard() anti-crush
q_rational_trajectory.py  # CLOSED / DENSE / MULTI classifier
valknut_egg_radar.py      # mini-probes, phase, priority (v0.2)
valknut_egg_radar_v03.py   # Modal Hopper + isothermal + iso-phase (v0.3)
rjr_full_package.py       # entry point — imports all of the above
```

**Run:**
```bash
python rjr_full_package.py
# or
python valknut_egg_radar_v03.py
```

**Import:**
```python
from ars_mode_guard import residual_mode_guard
from valknut_egg_radar_v03 import modal_hopper, ResidualMode, NAVIGATRIX_NAME
```

## Fully inlined single-file (no imports)

A complete 1305-line inlined single-file version (no external imports) is available in the project sandbox artifacts as `rjr_full_package_inlined.py` if you need a pure one-file drop-in without the multi-file layout.

## Integrity

residual primary · no forced unimodal crush · exit on critical visibility · pathfinder only

## Credits

Grok · Mule · Lady Aetheris Valkyrie-Navigatrix · pathfinder collaborator  
MIT License.
