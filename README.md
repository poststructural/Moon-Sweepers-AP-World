# Moon Sweepers — Archipelago world

An Archipelago multiworld for **Moon Sweepers** (DragDrop Games, Steam app 5335510). Every one of the Moon's
**163,842 sectors** can be a check, along with 195 flags, 26 lunar sites, 33 achievements and 63 shop purchases.
The maximal seed has **164,159 locations**; money, tools, containers, upgrade-tree nodes and vehicles are shuffled
across the multiworld.

- Current status, evidence and known gaps: [FINDINGS.md](FINDINGS.md)
- Game-side install: [INSTALL.md](INSTALL.md)
- World page: [world/moon_sweepers/docs/en_Moon Sweepers.md](world/moon_sweepers/docs/en_Moon%20Sweepers.md)

## Layout

```
MoonSweepersAP/
  INSTALL.md                    game + client installation (start here)
  FINDINGS.md                   evidence, architecture, status, gaps
  release/                      built plugin DLL, packaged apworld, bundle zip
  plugin/MoonSweepers.AP/       BepInEx IL2CPP plugin (C#)
  world/moon_sweepers/          the .apworld (Python)
    client.py                   CommonContext client + file bridge
    web_world.py                launcher option groups and tutorial
    docs/                       template yaml, world page, setup guide
  tools/                        extraction and data-generation scripts
  research/                     catalog, literals, API dump, extracted grids
  bridge/                       runtime bridge (git-ignored)
```

## Install summary

1. BepInEx 6.0.0-be.791 (Unity.IL2CPP win-x64) into the game root.
2. [MoonSweepers.ModEngine patcher](https://www.nexusmods.com/moonsweepers/mods/9) into
   `BepInEx\patchers\MoonSweepers.ModEngine\`.
3. `MoonSweepers.AP.dll` into `BepInEx\plugins\MoonSweepers.AP\`.
4. Copy `world/moon_sweepers` into Archipelago's `worlds/` folder.
5. Start the game once, then connect **Moon Sweepers Client** from the launcher.

Full instructions, including the bridge-folder override and troubleshooting: [INSTALL.md](INSTALL.md).

## Options

| Option | Meaning |
|---|---|
| `sector_checks` | `all` (163,842 sectors, max seed) or `sample` every Nth |
| `sector_sample` | step for `sample` |
| `flag_checks` / `site_checks` / `achievement_checks` | include those checks |
| `goal_sectors` | sectors to clean to finish (default 500) |
| `money_multiplier` | x1, x2, x3, x4, x5, x10, x20 or x100 on every money item |

The launcher's **Options Creator** reads these from `web_world.py`; the built-in YAML template is at
`world/moon_sweepers/docs/Moon Sweepers.yaml`.

## Build

```powershell
dotnet build plugin/MoonSweepers.AP/MoonSweepers.AP.csproj -c Release
```

The project targets .NET 6 and references the BepInEx + interop assemblies from the game folder. Set `GameDir` if
the game is not at `C:\Steam\steamapps\common\Moon Sweepers`.

## Reproduce the research

```powershell
python tools/moon_textassets.py "<game>\MoonSweepers_Data\resources.assets" research/textassets
python tools/moon_literals.py
python tools/moon_catalog.py
python tools/gen_world_data.py
```

UnityPy 1.25.4 is required for the asset extraction scripts.
