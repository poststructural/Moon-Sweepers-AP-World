# Moon Sweepers — Archipelago world

An Archipelago multiworld for **Moon Sweepers** (DragDrop Games, Steam app 5335510), built around the game's
sector and region completion events.

## Status

Research / feasibility. See [FINDINGS.md](FINDINGS.md).

Headline numbers from the shipped build:

| Check source | Count |
|---|---:|
| Hex sectors | 163,842 |
| Region bounties | 40,962 |
| Country flags | 195 |
| Lunar sites | 26 |
| Achievements | 33 |
| **Total** | **~205,091** |

## Layout

```
MoonSweepersAP/
  FINDINGS.md            feasibility, evidence, architecture, risks
  research/              extracted catalog + game data notes
  tools/                 extraction and generation scripts
  world/moon_sweepers/   the .apworld (planned)
  MoonSweepers.AP/       BepInEx IL2CPP plugin (planned)
  client/                Python bridge/client (planned)
```

The game install and `BepInEx` folder are intentionally not committed.

## Game-side hook

BepInEx 6.0.0-be.791 (Unity.IL2CPP win-x64) plus the community `MoonSweepers.ModEngine` preloader patcher,
which regenerates interop assemblies from the live runtime for Unity 6000.6 / metadata v108.

## Reproduce the research

```powershell
# extract RegionGrid + landmark assets from the shipped build
python tools/moon_textassets.py "<game>\MoonSweepers_Data\resources.assets" research/textassets

# recover the IL2CPP string literals
python tools/moon_literals.py

# rebuild the catalog
python tools/moon_catalog.py
```

UnityPy 1.25.4 is required for the asset extraction scripts.
