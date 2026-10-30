# Moon Sweepers Archipelago — v0.1.0-beta.2

> **AI disclosure:** AI was used to help develop this Archipelago mod.

Beta 2 fixes the Archipelago version requirement. **0.6.8 is the current release**, so the world now declares
`minimum_ap_version: 0.6.8` instead of 0.6.9. The manifest format (`compatible_version: 7`) is unchanged and is
what 0.6.8 already expects.

Everything else is the same as beta 1.

## Highlights

- **163,842 sector checks**; maximal seed **164,159 locations** with flags, lunar sites, achievements and shop
  purchases.
- **Money, tools, containers, upgrade-tree nodes and vehicles** are shuffled as items.
- **Shop purchases are checks.**
- **Money multiplier**: x1, x2, x3, x4, x5, x10, x20, x100.
- **Options Creator + Client** appear in the Archipelago Launcher.
- Goal is configurable (`goal_sectors`, default 500).

## What's in this release

| File | Contents |
|---|---|
| `MoonSweepers-AP-0.1.0.zip` | everything below in one bundle |
| `MoonSweepers.AP.dll` | BepInEx IL2CPP plugin |
| `moon_sweepers.apworld` | packaged world (folder install recommended) |
| `moon_sweepers/` | unpacked world folder (copy into Archipelago `worlds/`) |

## Requirements

- Moon Sweepers (Steam app 5335510), current Unity 6000.6 / IL2CPP metadata v108 build.
- BepInEx **6.0.0-be.791**, Unity.IL2CPP **win-x64**.
- [MoonSweepers.ModEngine patcher](https://www.nexusmods.com/moonsweepers/mods/9).
- Archipelago **0.6.8+**.

## Install (short)

1. Extract BepInEx into the game root.
2. Put the patcher DLL at `BepInEx\patchers\MoonSweepers.ModEngine\MoonSweepers.ModEngine.dll`.
3. Put `MoonSweepers.AP.dll` at `BepInEx\plugins\MoonSweepers.AP\MoonSweepers.AP.dll`.
4. Copy `moon_sweepers/` into Archipelago's `worlds/` folder.
5. Start the game once, then launch **Moon Sweepers Client**.

Full instructions, bridge-folder override and troubleshooting: `INSTALL.md` in the bundle
([INSTALL.md](https://github.com/poststructural/Moon-Sweepers-AP-World/blob/main/INSTALL.md)).

## Known limitations (beta)

- The maximal seed generates in ~3 minutes and is a stress/record seed, not a normal playthrough. Use
  `sector_checks: sample` for regular play.
- The `.apworld` zip loader in this Archipelago snapshot is unreliable; the folder form in `worlds/moon_sweepers/`
  is the supported install.
- The plugin tracks AP state in the bridge folder, not in the save itself. Loading a different save on the same
  bridge replays checks (the server dedupes them).
- Flags and sites are polled from active scene objects; a distant, unstreamed landmark may be missed until it loads.
- One AP slot sees all crew sector completions. A second player slot for co-op is not wired yet.
- The game's own "Region Bounty" is an upgrade node, not a second check tier; the real maximum is 164,159, not 205k.

## Changes since beta 1

- `minimum_ap_version` lowered from 0.6.9 to **0.6.8**.
- INSTALL and release notes updated to 0.6.8.
- Repackaged release assets.
