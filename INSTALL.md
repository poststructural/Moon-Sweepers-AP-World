# Installing the Moon Sweepers Archipelago mod

> **AI disclosure:** AI was used to help develop this Archipelago mod.

This guide covers the game side, the Archipelago side and the bridge between them. It is written for the current
Steam build (**Unity 6000.6.0f1, IL2CPP metadata v108**). If Moon Sweepers updates, re-check the BepInEx patcher
first; the game has shipped metadata changes before.

---

## 0. What you need

| Thing | Where |
|---|---|
| Moon Sweepers | Steam, app **5335510** |
| BepInEx **6.0.0-be.791**, Unity.IL2CPP **win-x64** | <https://builds.bepinex.dev/projects/bepinex_be/791> |
| **MoonSweepers.ModEngine** patcher | <https://www.nexusmods.com/moonsweepers/mods/9> |
| `MoonSweepers.AP.dll` | this repo, `release/MoonSweepers.AP.dll` (or build it) |
| Archipelago 0.6.8+ | the client and `worlds/` folder |
| Python 3.12 | only needed if you run the client from source |

> **Back up your save first.** Saves live in
> `%USERPROFILE%\AppData\LocalLow\DragDrop Games\Moon Sweepers`. The mod does not edit saves directly, but a
> playtest with a new seed can overwrite progress in the slot you load.

---

## 1. Install BepInEx

1. Close Moon Sweepers and Steam's game process.
2. Download **BepInEx-Unity.IL2CPP-win-x64-6.0.0-be.791+b782da4.zip**.
3. Extract it **into the game root**, next to `MoonSweepers.exe`:
   `C:\Steam\steamapps\common\Moon Sweepers\`.
4. You should now have:

```
Moon Sweepers\
  BepInEx\
    core\
    plugins\
  dotnet\
  winhttp.dll
  doorstop_config.ini
  MoonSweepers.exe
```

Do **not** use the Mono, .NET Framework or CoreCLR BepInEx builds. The patcher only works with the IL2CPP build.

---

## 2. Install the patcher

The game uses IL2CPP metadata **v108**. BepInEx's bundled Cpp2IL stops at v106, so BepInEx alone loads zero
plugins. The community patcher generates interop from the running game instead.

1. Download **MoonSweepers BepInEx Patcher** from Nexus mod 9.
2. Extract it so the DLL ends up exactly here:

```
Moon Sweepers\BepInEx\patchers\MoonSweepers.ModEngine\MoonSweepers.ModEngine.dll
```

3. Do not rename the folder or the DLL. The patcher finds itself by path.

Optional: the BepInEx console window is noisy. You can disable it in
`BepInEx\config\BepInEx.cfg` under `[Logging.Console]` → `Enabled = false`. Logs still go to
`BepInEx\LogOutput.log`.

---

## 3. Install the plugin

Copy the built plugin into its own folder:

```
Moon Sweepers\BepInEx\plugins\MoonSweepers.AP\MoonSweepers.AP.dll
```

Use `release/MoonSweepers.AP.dll` from this repo, or build it:

```powershell
dotnet build plugin/MoonSweepers.AP/MoonSweepers.AP.csproj -c Release
```

If the game is not installed at the default path, pass the folder:

```powershell
dotnet build plugin/MoonSweepers.AP/MoonSweepers.AP.csproj -c Release -p:GameDir="D:\Games\Moon Sweepers"
```

The build needs no NuGet packages; it references the BepInEx and interop DLLs already in the game folder.

---

## 4. First launch (interop generation)

1. Start Moon Sweepers normally from Steam.
2. The first start takes about 15 seconds longer while the patcher writes interop assemblies.
3. `BepInEx\LogOutput.log` should contain:

```
[MoonSweepers ModEngine] Interop assemblies generated in ...
[Message:   BepInEx] Chainloader startup complete
[Info   :Moon Sweepers AP] MOONAP plugin 0.1 loaded; bridge=...
```

A BepInEx error about **"Unsupported metadata version 108"** is expected from the stock Cpp2IL step; the patcher
takes over immediately after it. If you see `0 plugins to load`, the plugin DLL is in the wrong folder or the
patcher is missing.

4. Start or load a save. Once the Moon is loaded, the plugin creates the bridge folder and writes `status.json`.

---

## 5. Install the Archipelago world

Copy the whole world folder into Archipelago:

```
Archipelago\worlds\moon_sweepers\
  __init__.py
  archipelago.json
  client.py
  data.py
  ...
```

Or copy `release/moon_sweepers.apworld` into `Archipelago\custom_worlds\` and restart the launcher. If the launcher
does not list the world from the `.apworld`, unzip it into `worlds\moon_sweepers\` instead — the folder form always
works.

Restart the Archipelago Launcher. You should see:

- **Moon Sweepers** in the game list.
- **Moon Sweepers Client** in the client/tools list.
- The options under **Options Creator** (Checks, Goal, Money Multiplier).

---

## 6. Generate a seed

Minimal solo YAML:

```yaml
name: Jerrod
game: Moon Sweepers
Moon Sweepers:
  sector_checks: sample
  sector_sample: 10
  goal_sectors: 500
  money_multiplier: x10
```

- `sector_checks: all` gives the maximal **164,159-location** seed and takes about three minutes to generate.
- `sector_checks: sample` with `sector_sample: 10` is a normal playable seed (~16k sector checks).
- `money_multiplier`: `x1`, `x2`, `x3`, `x4`, `x5`, `x10`, `x20`, `x100`. It scales every money item, for faster
  early tools and upgrades.

Generate from the launcher or:

```powershell
python Generate.py --player_files_path Players --outputpath Output
```

---

## 7. Start the server and client

### Launcher (recommended)

1. Host the generated seed in the launcher, or run `MultiServer.py <seed>.zip`.
2. Launch **Moon Sweepers Client** from the launcher.
3. Enter the server address and the **slot name** from the YAML.

### Command line

```powershell
python -m worlds.moon_sweepers.client `
  --connect localhost:38281 `
  --name Jerrod `
  --nogui
```

The client connects to Archipelago on one side and to the plugin through the bridge folder on the other.

### Bridge folder

By default the plugin uses:

```
Moon Sweepers\BepInEx\config\moon_ap\
```

If Python cannot write there (sandboxed install, read-only game folder, or the launcher runs as another user),
create a text file:

```
Moon Sweepers\BepInEx\config\moon_ap_path.txt
```

containing a writable path, for example:

```
C:\MoonSweepersAP\bridge
```

Then start the client with the same folder:

```powershell
python -m worlds.moon_sweepers.client --connect localhost:38281 --name Jerrod --bridge "C:\MoonSweepersAP\bridge" --nogui
```

The bridge uses four files:

| File | Direction | Contents |
|---|---|---|
| `checks.jsonl` | plugin → client | sector / flag / site / achievement / purchase checks, goal |
| `items.jsonl` | client → plugin | received items, in order |
| `slot.json` | client → plugin | goal, grants, purchase location names, money values |
| `status.json` | plugin → client | live progress (sectors completed, items applied) |

---

## 8. Verify it is working

1. Load a save. `status.json` should update within a second:

```json
{"player":"local","completed":0,"goal":500,"sectors":163842,"checks_sent":12,...}
```

2. The client log shows `Wrote slot data` and `Queued N item(s) for the game.`
3. The server logs location checks and item sends.
4. In game, the wallet changes when money items arrive; tools/upgrades appear equipped or owned.
5. Finish a sector: `Sector 000001` (or whichever) appears in the server log.

---

## 9. Troubleshooting

| Symptom | Fix |
|---|---|
| `0 plugins to load` | Plugin DLL not under `BepInEx\plugins\MoonSweepers.AP\`, or patcher DLL missing/misnamed |
| `Unsupported metadata version 108` | Expected; confirm the patcher is present and log ends with `Chainloader startup complete` |
| `MOONAP plugin loaded` but no `status.json` | World not loaded yet (main menu), or bridge folder override points somewhere else |
| Client connects but no checks | Client and plugin must use the same bridge folder; check `slot.json` exists |
| `Permission denied` writing bridge files | Use `moon_ap_path.txt` to move the bridge to a writable folder and pass `--bridge` |
| Purchases do not send checks | Shop purchases are detected through `CrewPurchase`; buy through the normal shop UI |
| Wrong or doubled money | `money_multiplier` applies to filler money; old seeds use x1 |
| Game updated and mods stopped | Steam restored the original exe/dlls. Reinstall BepInEx + patcher; the patcher regenerates interop on the next start |
| Interop fails after an update | Check the patcher page for a new release; metadata version may have changed again |

---

## 10. Uninstall

1. Delete `BepInEx\plugins\MoonSweepers.AP\`.
2. To remove the mod loader entirely, delete `BepInEx\`, `dotnet\`, `winhttp.dll`, `doorstop_config.ini`,
   `.doorstop_version` and `changelog.txt` from the game root.
3. Remove `worlds\moon_sweepers\` from Archipelago.
4. Saves are untouched; delete them from
   `%USERPROFILE%\AppData\LocalLow\DragDrop Games\Moon Sweepers` if you want a clean slate.
