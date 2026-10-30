# Moon Sweepers + Archipelago — feasibility findings

Date: 2026-10-30. Status: research only. Nothing installed into the game, no game files changed.
Build inspected: `MoonSweepersAP\Moon Sweepers` (Unity 6000.6.0f1, IL2CPP metadata v108, namespace `MoonCleaners`).

## Verdict

**Feasible, and the check count is real.** Moon Sweepers exposes 163,842 individual sector completions, plus a
second tier of 40,962 region bounties, before landmarks, achievements or shop purchases. That is roughly
**205,000 locations** — likely the largest Archipelago world by an order of magnitude. The hard part is not
hooking the game (the community has already solved IL2CPP v108 with a BepInEx patcher); it is making a 205k
seed generate and stay playable, and confirming the region-bounty tier in-game.

## Build facts

| Fact | Evidence |
|---|---|
| Unity 6000.6.0f1 | version string in `MoonSweepers_Data\globalgamemanagers` |
| IL2CPP, metadata v108 | `global-metadata.dat`: magic `FAB11BAF`, version `108` |
| `Assembly-CSharp`, namespace `MoonCleaners` | `RuntimeInitializeOnLoads.json` |
| Steam app 5335510, 1–16 players, solo supported | Steam store page |
| No install/save on this PC | `C:\Steam\steamapps\libraryfolders.vdf` has no 5335510; no `DragDropGames` folder in `AppData\LocalLow` |

The folder in `MoonSweepersAP` is a copied build, not a Steam install, and this PC has never run it. That matters
for the next milestone (see *What I need*).

## The 200k check count

### Sectors — 163,842, confirmed

The game says it outright:

- `There are 163,842 sectors. Nobody has counted twice.`
- `One clean line. Only 163,841 sectors to go.`
- `The Moon is split into hexagonal sectors. Clean one completely for a bonus.`
- `Every sector you finish pays a bonus. So does every flag you raise and every lunar site you survey.`

The world data agrees. `RegionGrid_L7` is a binary `MRG1` grid holding exactly **163,842** unit-vector cell
centres (12 bytes each). The counts across all eight LODs follow `10 * 4^level + 2`:

| Grid | Cells |
|---|---:|
| L0 | 12 |
| L1 | 42 |
| L2 | 162 |
| L3 | 642 |
| L4 | 2,562 |
| L5 | 10,242 |
| L6 | 40,962 |
| L7 | 163,842 |

### Regions — 40,962, strongly inferred

There is a second reward tier called a **Region Bounty**:

- `A bonus each time you finish cleaning a whole region.`
- `+${0} per region cleared`
- `{0} regions cleaned`
- `Region Bounty`

`RegionGrid_L6` has 40,962 cells, and 163,842 is exactly `4 * 40,962 - 6` (the pole/edge correction in the
`10*4^L+2` series). In other words the L6 grid is the region layer and each region contains four L7 sectors.
The `RegionGrid_L*` files are separate LOD point sets, so the exact sector→region mapping still needs a probe,
but the 4:1 structure and the separate "regions cleaned" counter are strong evidence that sector completion and
region bounty are two different checks.

### Everything else

| Source | Count | Evidence |
|---|---:|---|
| Sectors | 163,842 | game text + `RegionGrid_L7.bin` |
| Region bounties | 40,962 | `RegionGrid_L6.bin` + region bounty text |
| Country flags | 195 | `flags.txt` (`flags` array) |
| Lunar sites | 26 | `sites.txt` (impact, landing, rover, crash) |
| Achievements | 33 | `ACH_*` strings (`ACH_FIRST_SWEEP` … `ACH_MOON_CLEAN_100`) |
| **Subtotal** | **205,091** | |

Shop and upgrade-tree locations (tools, containers, matrix nodes, vehicles, vehicle upgrades) add roughly
50–70 more, so a maximal seed lands around **205,150** locations.

Even if the region tier turns out to be the same event as the sector bonus, **163,842** is still far beyond any
AP world I can find (typical large worlds are hundreds to a few thousand checks), so the headline does not
depend on the region interpretation.

### Caveat

The region-bounty tier is the one number that needs in-game confirmation. The L6 grid and the UI text are
convincing, but I have not seen a region bounty fire. Treat 205k as "expected, pending probe" and 163,842 as
"confirmed".

## What a check would be

Natural checks, all of which the game already celebrates in its own HUD:

- **Sector complete** — `SECTOR COMPLETE`, `{0} SECTORS CLEAN`, per-sector bonus.
- **Region bounty** — `Region Bounty`, `{0} regions cleaned`.
- **Flag raised** — 195 country flags scattered on the Moon (`ACH_*`/UI text mentions every flag).
- **Lunar site surveyed** — 26 real landers/rovers/crash sites (`Lunar sites are real landers, rovers and crash sites`).
- **Achievement** — 33 Steam achievements, if we hook `MoonAchievements`.
- **Shop/upgrade purchases** — each tool, container upgrade, upgrade-matrix node and vehicle.
- **Vehicle upgrades** — speed, hopper, boost, cruise control, suction, lights per vehicle.

## What items could be

Progression (from the game's own tool/upgrade names):

- **Tools:** toothbrush (start), hand brush, nail brush, detail brush, angled edge brush, household broom,
  wide broom, extra wide broom, telescopic brush, rotary brush, hand vacuum, backpack vacuum.
- **Container upgrades** for each tool (the game has a "bigger dust container" upgrade for toothbrush, hand
  brush, nail brush, household broom, wide broom, extra wide broom).
- **Upgrade matrix nodes:** thruster pack, helmet lamp, battery/recharge, movement speed, reach, suction,
  bulk deals, etc. ("Unlock the connected upgrades first", "The upgrade matrix").
- **Vehicles:** push sweeper ($300), ride-on sweeper ($1,000), crew transport van ($2,000), lunar sweeper
  ($2,500), mega vacuum rover ($6,000).
- **Vehicle upgrades:** speed, hopper, boost, cruise control, suction, lights.

Useful/filler: money injections (shared crew wallet) and dust deliveries. Traps: a dust storm, a tax bill, or a
temporary tool lockout.

Goal options: clean N sectors; clean the whole Moon; earn $1,000,000; unlock every vehicle; N regions.

## Modding path — already solved by the community

Stock BepInEx 6 cannot load IL2CPP v108: its bundled Cpp2IL stops at v106. The fix is public and proven:

- **BepInEx 6.0.0-be.791, Unity.IL2CPP win-x64** (`b782da4`).
- **MoonSweepers.ModEngine** preloader patcher (Nexus mod 9) — generates Interop assemblies from the live
  runtime instead of parsing `global-metadata.dat`, fixes the changed `Il2CppClass` layout for Unity 6000.6, and
  repairs broken method references.
- It writes browseable dummy assemblies to `BepInEx\dummy` and supports Harmony patches, `ClassInjector` and
  custom MonoBehaviours. 25 mods already depend on it.

That means a BepInEx plugin can subscribe to `MoonRegions` events (`RegionCompleted`, `RegionBountyPaid`,
`OnRegionCommitted`), read `CompletedRegionCount` / `TouchedRegionCount` / `RegionRemainingDust`, and call the
game's own money/tool/vehicle APIs. No memory hacking, no file patching of the game itself.

## Proposed architecture (same shape as ME1 / TFM2)

```
MoonSweepersAP/
  MoonSweepers.AP/          BepInEx IL2CPP plugin (C#)      [M3]
  client/                   MoonSweepersClient (Python)     [M4]
  world/moon_sweepers/      the .apworld (Python)           [M4]
  research/                 extracted data (this study)
  installer/                BepInEx + patcher + plugin      [M5]
```

1. **Plugin** — Harmony hooks sector/region completion, writes checks to a localhost socket, applies received
   items (money, tool unlock, vehicle unlock, upgrade node), keeps AP state in a sidecar JSON per save slot.
2. **Python client** — `CommonClient`: AP websocket on one side, plugin socket on the other, item order and
   reconnect handling.
3. **apworld** — data-driven locations (sectors/regions generated from the grids), regions, options, logic,
   slot data. No giant static tables; 163k locations are generated from the L7 grid at generation time.
4. **Installer** — BepInEx be.791 + patcher + plugin + client, packaged like ME1/TFM2.

## Scale risks (the real work)

1. **AP generation at 205k.** AP's fill is batched, but 205k locations is far outside anything it has been
   tested on. Needs a benchmark before promising `max`. Fallback: cap the maximal preset or ship a custom
   fast-fill path.
2. **Datapackage/multidata size.** ~205k location names is roughly 10–20 MB of JSON. The server is fine; the
   web tracker likely is not. Plan a "no tracker" note for max seeds.
3. **Playtime.** Cleaning 163k sectors is not a normal run. Default must be a sampled subset; `max` is the
   record/meme preset.
4. **Item flood.** 205k items means ~205k filler grants. Batch money silently, no per-item popup.
5. **Co-op semantics.** Crew members' sector completions would count for the AP slot (shared world). Needs a
   policy/option.
6. **Game updates.** The patcher regenerates on `GameAssembly.dll` changes, but pin the build and re-test after
   patches.
7. **No runnable install here.** The copied build needs Steam ownership; dummy assemblies and probes require a
   real launch.

## Proposed density presets

| Preset | Locations | Use |
|---|---:|---|
| `standard` | ~1,000–2,000 | normal playable seed: sampled sectors/regions + all landmarks/achievements/shop |
| `dense` | ~10,000 | every Nth sector + regions |
| `max` | ~205,000 | every sector + every region + everything; the record |

Default should be `standard`. `max` exists for the "most checks of any AP world" run and for stress testing.

## Milestones (each needs a go-ahead)

- **M0 — research (done):** build facts, grid extraction, check-count evidence, catalog.
- **M1 — runnable probe:** install BepInEx be.791 + patcher on a machine that owns the game, launch once,
  collect `BepInEx\dummy\Assembly-CSharp.dll`, decompile the region/save/money/tool APIs.
- **M2 — read-only probe plugin:** log sector completions, region bounties, save fields and tool/vehicle state;
  confirm the 205k tier and the exact event signatures.
- **M3 — AP plugin v0:** checks out, money in, sidecar state, bridge to Python.
- **M4 — apworld + client:** regions/items/options/logic; generation benchmark at `standard`, `dense`, `max`.
- **M5 — playtest + package.**

## What I need from you

1. **Is Moon Sweepers installed through Steam on a PC we can run?** This PC only has the copied build in
   `MoonSweepersAP\Moon Sweepers`, and `C:\Steam` does not list app 5335510. If it is on another machine, that
   machine is where M1/M2 have to happen.
2. **The patcher zip.** Download [MoonSweepers BepInEx Patcher](https://www.nexusmods.com/moonsweepers/mods/9)
   and drop it in the folder (or tell me it is fine to install BepInEx + patcher into the copied build).
3. **Default density and goal.** Is `standard` the default with `max` as an option, or do you want `max` as the
   default for the first seed?

## Files from this study

- [moon_catalog.json](research/moon_catalog.json) — counts, 26 sites, 195 flags, 33 achievements, tool/vehicle lists.
- [moon_literals.txt](research/moon_literals.txt) — 15,491 extracted English strings (UI text, hints, achievement IDs).
- [RegionGrid_L7.bin](research/textassets/RegionGrid_L7.bin) / [L6](research/textassets/RegionGrid_L6.bin) — sector/region grids.
- [sites.txt](research/textassets/sites.txt) / [flags.txt](research/textassets/flags.txt) — landmark data.
- [moon_sector_region.npy](research/moon_sector_region.npy) — nearest L6 region for every L7 sector (first-pass mapping).
- Extraction scripts: `tools/moon_inspect.py`, `moon_raw.py`, `moon_inventory.py`, `moon_textassets.py`,
  `moon_literals.py`, `moon_catalog.py`.
