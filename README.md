# Moon Sweepers — Archipelago world

An Archipelago multiworld for **Moon Sweepers** (DragDrop Games, Steam app 5335510), built around the game's
163,842 sector completion events, shop purchases, landmarks and achievements.

## Status

Working prototype. Live-tested end to end against a local Archipelago server: sector/achievement checks, money,
tool, container, upgrade and vehicle grants.

| Check source | Count |
|---|---:|
| Sectors | 163,842 |
| Country flags | 195 |
| Lunar sites | 26 |
| Achievements | 33 |
| Shop purchases | 63 |
| **Max locations** | **164,159** |

A max seed generates in about three minutes. See [FINDINGS.md](FINDINGS.md) for evidence, the live probe output and
the known gaps.

## Layout

```
MoonSweepersAP/
  FINDINGS.md               evidence, architecture, status, gaps
  plugin/MoonSweepers.AP/   BepInEx IL2CPP plugin (C#)
  world/moon_sweepers/      the .apworld (Python)
    client.py               CommonContext client + file bridge
    web_world.py            launcher option groups and tutorial
    docs/                   template yaml, world page, setup guide
  tools/                    extraction and data-generation scripts
  research/                 catalog, literals, API dump, extracted grids
  bridge/                   runtime bridge (git-ignored)
```

The game install and `BepInEx` folder are intentionally not committed.

## Install (game side)

1. BepInEx 6.0.0-be.791 (Unity.IL2CPP win-x64).
2. [MoonSweepers.ModEngine patcher](https://www.nexusmods.com/moonsweepers/mods/9) in
   `BepInEx\patchers\MoonSweepers.ModEngine\`.
3. `MoonSweepers.AP.dll` in `BepInEx\plugins\MoonSweepers.AP\`.

## Run

1. Put `world/moon_sweepers` (or a zipped `.apworld`) in Archipelago's `worlds/` folder and restart the launcher.
2. Generate a seed. The **Moon Sweepers Client** appears in the launcher's client list; the built-in
   **Options Creator** picks up the option groups from `web_world.py`.
3. Connect the client, then start or load a save.

## Reproduce the research

```powershell
python tools/moon_textassets.py "<game>\MoonSweepers_Data\resources.assets" research/textassets
python tools/moon_literals.py
python tools/moon_catalog.py
python tools/gen_world_data.py
```

UnityPy 1.25.4 is required for the asset extraction scripts.
