# Moon Sweepers + Archipelago — findings and status

Date: 2026-10-30. Status: **working prototype**. Game build: Unity 6000.6.0f1, IL2CPP metadata v108,
namespace `MoonCleaners`; Steam app 5335510.

## Verdict

**Feasible, implemented, and running.** Moon Sweepers exposes **163,842 individual sector completions**. With
country flags, lunar sites, achievements and shop purchases the maximal seed has **164,159 locations** — still far
beyond any other Archipelago world I can find. The 200k figure from the first pass was wrong: the "Region Bounty"
is an upgrade-tree node (`eco.bounty`), not a second tier of checks. A live probe of `MoonWorld.regionStates`
confirmed 163,842 regions at level 7, of which 12 start empty.

## Confirmed counts

| Source | Count | Evidence |
|---|---:|---|
| Sectors | 163,842 | in-game text (`There are 163,842 sectors`) + `RegionGrid_L7` |
| Country flags | 195 | `flags.txt` |
| Lunar sites | 26 | `sites.txt` |
| Achievements | 33 | `ACH_*` literals |
| Shop purchases | 63 | 5 tools + 18 container tiers + 35 tree levels + 5 vehicles |
| **Total** | **164,159** | |

Live probe output from a loaded save:

```
MOONAP regions=163842 level=7 even=True states=163842 bank=163842
       initial=163842 remaining=163842 completed=0 touched=0 empty=12 wallet=0
MOONAP state histogram 0=163830 2=12
```

`regionStates` is the authoritative per-sector state array; state 2 means the sector is clean. The 12 sectors that
start at 2 are included as locations and are sent on world load.

## What works (verified live)

- **Sector checks** — polling `MoonWorld.regionStates` and diffing each 0.5 s; transitions to 2 send
  `Sector 000001` … `Sector 163842`.
- **Existing checks** — on world load the plugin sends the 12 empty sectors plus any already-unlocked
  achievements, so a resumed save does not lose credit.
- **Achievement checks** — polling `MoonAchievements.unlocked`.
- **Purchase checks** — Harmony postfix on `MoonWorld.CrewPurchase` (tools, containers, tree nodes) and
  `TryBuyVehicle`.
- **Money items** — `MoonWorld.DevAddMoney` (verified in-game: wallet went $1.50 → $4.00).
- **Tree upgrades** — direct `MoonWorld.PlayerUpgradeState(player).tree` edit + `SetPlayerUpgradeState` +
  `CommitUpgrade` (verified: `clean.width` 1 → 2 and persisted).
- **Containers** — same path via `.containers` (verified: `hand_brush` tier 1 → 2).
- **Tools** — same path via `.tools` + `TryAssignTool` (verified: "Equipped in slot 1").
- **Vehicles** — `TryBuyVehicle`.
- **Goal** — `CompletedRegionCount >= goal_sectors` writes a goal event; the client sends `CLIENT_GOAL`.
- **End-to-end** — local server + client + plugin: 16 checks sent, 17 items received and applied.

## Why the purchase APIs needed a fallback

`TryPurchaseTool` / `TryPurchaseTreeNode` / `TryPurchaseContainer` are gated by shop state and money
("This tool is unavailable", "Not enough money"). `CrewPurchase` is also gated. The reliable path is
`MoonWorld.PlayerUpgradeState(player)` — the authoritative `UpgradeState` with `tools`, `containers` and `tree`
sorted dictionaries — followed by `SetPlayerUpgradeState`, `CommitUpgrade`, and `TryAssignTool` for tools.
Item grants use that path; purchase checks still fire from the game's own `CrewPurchase` when the player buys.

## Architecture

```
MoonSweepersAP/
  plugin/MoonSweepers.AP/       BepInEx IL2CPP plugin (C#)
  world/moon_sweepers/          the .apworld (Python)
    client.py                   CommonContext client, file bridge to the plugin
    web_world.py                launcher metadata (option groups, tutorial)
    docs/                       template yaml, world page, setup guide
  bridge/                       runtime bridge (git-ignored)
  tools/                        extraction and data-generation scripts
  research/                     extracted catalog and API dump
```

The plugin and Python client exchange four files in a bridge folder:

- `checks.jsonl` — plugin → client (checks, goal)
- `items.jsonl` — client → plugin (received items, in order)
- `slot.json` — client → plugin (goal, grants, purchase names, money values)
- `status.json` — plugin → client (live progress)

This keeps all AP protocol code in Python. The plugin only watches game state and calls the game's own methods.
`BepInEx\config\moon_ap_path.txt` can redirect the bridge to a writable folder (used here because the shell's
Python child processes are sandboxed to the workspace).

## Generation and scale

- Max seed (164,159 locations): **~170–180 s**, output zip **~1.2 MB**.
- Small sampled seed (481 locations): **~1 s**.
- Two-player max seed: ~170 s, 164,640 items.
- All locations are reachable from the start, so fill is trivial and progression balancing is skipped.

## Modding path

BepInEx 6.0.0-be.791 (Unity.IL2CPP win-x64) plus the community **MoonSweepers.ModEngine** preloader patcher
(Nexus mod 9). The patcher generates interop from the live runtime because stock Cpp2IL stops at metadata v106;
it also fixes the Unity 6000.6 `Il2CppClass` layout and repairs broken method references. Harmony and
`ClassInjector` work; the plugin uses Harmony and direct IL2CPP calls.

## Known gaps

- Flags and sites are polled with `FindObjectsOfType<MoonLandmarkFlag/MoonLunarSite>`; only active instances are
  seen. A distance/inactive flag may be missed until it streams in. A registry hook is the next improvement.
- No per-save AP state file yet; checks are deduped in memory and in `checked.txt`. A save rollback or second
  save on the same bridge will resend checks (the server dedupes).
- Tool items are granted to slot 1 and may overwrite the player's preferred belt layout.
- The client currently needs `--bridge` when the game folder is not writable by Python; the launcher component
  does not pass that automatically yet.
- Co-op: one AP slot sees all crew sector completions. A second AP slot for a second player is not wired.

## Files

- [moon_catalog.json](research/moon_catalog.json)
- [moon_literals.txt](research/moon_literals.txt)
- [api_dump.txt](research/api_dump.txt)
- [sites.txt](research/textassets/sites.txt), [flags.txt](research/textassets/flags.txt)
- [RegionGrid_L7.bin](research/textassets/RegionGrid_L7.bin), [L6](research/textassets/RegionGrid_L6.bin)
- Extraction scripts: `tools/moon_*.py`, `tools/gen_world_data.py`, `tools/dump_api.ps1`
