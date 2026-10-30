# Moon Sweepers setup guide

## Requirements

- Moon Sweepers (Steam app 5335510), current build (Unity 6000.6 / IL2CPP metadata v108).
- [BepInEx 6.0.0-be.791, Unity.IL2CPP win-x64](https://builds.bepinex.dev/projects/bepinex_be/791).
- The [MoonSweepers.ModEngine patcher](https://www.nexusmods.com/moonsweepers/mods/9) (BepInEx cannot read
  metadata v108 without it).
- Python 3.12 with this apworld installed in Archipelago's `worlds/` folder.

## Install

1. Extract BepInEx into the game root.
2. Extract the patcher so the DLL is at
   `<game>\BepInEx\patchers\MoonSweepers.ModEngine\MoonSweepers.ModEngine.dll`.
3. Put `MoonSweepers.AP.dll` in `<game>\BepInEx\plugins\MoonSweepers.AP\`.
4. Run the game once. BepInEx logs `Chainloader startup complete`; interop is regenerated automatically.

## Play

1. Generate a seed with `Moon Sweepers` as the game.
2. Start `MoonSweepersClient` from the Archipelago Launcher, or run:
   `python -m worlds.moon_sweepers.client --connect <host>:<port> --name <slot> --bridge <game>\BepInEx\config\moon_ap --nogui`
3. Start or load a save. The plugin writes `status.json` in the bridge folder and queues existing checks.
4. Sectors you finish, flags you raise, sites you survey, achievements and shop purchases are sent as checks.
   Money and upgrades arrive as items and are applied automatically.

## Bridge folder

The plugin and client exchange four files in the bridge folder:

- `checks.jsonl` — plugin → client (checks and goal).
- `items.jsonl` — client → plugin (received items).
- `slot.json` — client → plugin (goal, grants, purchase names).
- `status.json` — plugin → client (progress).

If the game folder is not writable by the client, point `BepInEx\config\moon_ap_path.txt` at a writable folder
(for example the repository's `bridge/` folder) and pass the same folder to `--bridge`.
