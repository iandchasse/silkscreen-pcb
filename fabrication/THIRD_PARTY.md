# Third-party library files

The board **design** in this repository (schematic and PCB) is licensed **CERN-OHL-S-2.0**
(see [`../LICENSE`](../LICENSE)). A handful of component **library files** — symbols, footprints
and 3D models under `KiCad/9.0/3rdparty/` — were obtained from **SnapEDA**, **Ultra Librarian**
and **SamacSys / Component Search Engine**.

**What that means for licensing:**
- ✅ All three vendors permit *using* these parts in a design and distributing the resulting
  **board design under any license** — so the CERN-OHL-S license on this project is unaffected,
  and you may fabricate, use, sell and modify boards made from it.
- ⚠️ All three **restrict redistributing the raw model files** as a standalone, reusable PCB
  library. They are included here only for build convenience. **If you fork or redistribute this
  repo as a component library, re-download each part from its vendor** (links below).
- The board also builds without these files: symbols are cached in `silkscreen_pcb.kicad_sch`
  and footprints are embedded in `silkscreen_pcb.kicad_pcb`, so you can regenerate fab data even
  if the `3rdparty/` folder is absent.
- Manufacturer 3D STEP models (e.g. Hirose, TI) carry their own manufacturer terms.
- Everything else in the design uses **KiCad's standard libraries** (CC-BY-SA-4.0 with the
  library exception — freely redistributable).

## Vendored parts

| MPN | Ref(s) | Files provided | Source | Re-download |
|---|---|---|---|---|
| FH34SRJ-24S-0.5SH(50) | J2 | symbol, footprint, 3D | SnapEDA | https://www.snapeda.com/search/?q=FH34SRJ-24S-0.5SH |
| FH34SRJ-6S-0.5SH(50) | J3, J4 | symbol, footprint, 3D | SnapEDA | https://www.snapeda.com/search/?q=FH34SRJ-6S-0.5SH |
| PPPC062LJBN-RC | J6 | symbol, footprint | SnapEDA | https://www.snapeda.com/search/?q=PPPC062LJBN-RC |
| TPD4E1U06DBVR | U1, U6–U9 | symbol | SnapEDA | https://www.snapeda.com/search/?q=TPD4E1U06DBVR |
| TSD05CDYFR | CR1–CR3 (symbol only; CR1 is SMF6.5CA and CR2/CR3 use standard SOD-323 footprints) | symbol | SnapEDA | https://www.snapeda.com/search/?q=TSD05CDYFR |
| FS8205A | Q1 | symbol | Ultra Librarian | https://app.ultralibrarian.com/search?queryText=FS8205A |
| TPS923610DRLR | U10 | symbol, footprint | Ultra Librarian | https://app.ultralibrarian.com/search?queryText=TPS923610DRLR |
| MJTP1117 | SW1–SW5, SW7–SW11 (footprint) | footprint | SamacSys / Component Search Engine | https://componentsearchengine.com/search?term=MJTP1117 |
| microSD push-push (unified) | J7 | footprint (project-built), 3D model | GCT MEM2075 pad geometry + SHOU HAN TF PUSH DXF + FastEDA 3D (via Protoflow) | see note below |

Notes:
- `MJTP1117` contributes only the **footprint** (and 3D model); its symbol is KiCad standard
  (`Switch:SW_Push`). `SW6` uses a KiCad-standard MJTP1243 footprint. `L1` uses the KiCad-standard footprint
  `Inductor_SMD:L_APV_ANR5040` (and its standard 3D model), so no third-party inductor files are shipped.
- On 2026-09-18 unused vendored files were removed from the repository (the old `SRN3010C-100M` L1 footprint,
  the TSD05/TPD4E1U06/FS8205A footprints and 3D models, and the legacy KiCad-5 `MJTP1117` files) because nothing
  references them; re-download from the vendors above if you need them.
- `J1` (USB-C) and every passive/IC not listed above use **standard KiCad libraries** — no
  third-party terms apply.
- `J7`'s footprint `microSD_dualsource:microSD_PushPush_TFPUSH-MEM2075` is **project-built** in
  this repo (KiCad symbol is standard `Connector:Micro_SD_Card`). Its pad geometry was derived
  from GCT's official MEM2075 `.kicad_mod` and SHOU HAN's TF PUSH manufacturer DXF; the attached
  3D model (`TF-SMD_TF-PUSH.wrl`) is FastEDA-generated (obtained via Protoflow) and carries its
  generator's terms. The footprint is a dual-source land accepting either the SHOU HAN TF PUSH
  (LCSC C393941) or GCT MEM2075-00-140-01-A.
- `TPS923610DRLR`'s 3D model (`SOT563.STEP`) is the manufacturer's, added separately.
