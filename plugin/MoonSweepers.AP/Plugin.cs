using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using System.Text.Json;
using BepInEx;
using BepInEx.Logging;
using BepInEx.Unity.IL2CPP;
using HarmonyLib;
using MoonCleaners;
using UnityEngine;

namespace MoonSweepers.AP
{
    [BepInPlugin("moon.ap", "Moon Sweepers AP", "0.1.0")]
    public class MoonApPlugin : BasePlugin
    {
        internal static ManualLogSource Log2;
        internal static MoonApPlugin Instance;

        internal string BridgeDir;
        internal HashSet<string> Sent = new();
        internal SlotData Slot = new();
        internal DateTime SlotWrite = DateTime.MinValue;

        internal byte[] PrevStates;
        internal bool InitialSectors;
        internal bool GoalSent;
        internal long ItemOffset;
        internal int ItemsApplied;
        internal float NextTick;

        internal readonly Dictionary<string, int> NodeLevel = new();
        internal readonly Dictionary<string, int> ContainerTier = new();
        internal readonly HashSet<string> AchSeen = new();
        internal bool CatalogDumped;

        public override void Load()
        {
            Instance = this;
            Log2 = Log;
            BridgeDir = Path.Combine(Paths.ConfigPath, "moon_ap");
            var overrideFile = Path.Combine(Paths.ConfigPath, "moon_ap_path.txt");
            if (File.Exists(overrideFile))
            {
                var custom = File.ReadAllText(overrideFile).Trim();
                if (custom.Length > 0)
                    BridgeDir = custom;
            }
            Directory.CreateDirectory(BridgeDir);
            LoadChecked();
            LoadItemOffset();
            LoadSlot(force: true);
            Log.LogInfo($"MOONAP plugin 0.1 loaded; bridge={BridgeDir}; known checks={Sent.Count}");
            Harmony.CreateAndPatchAll(typeof(MoonApPlugin).Assembly);
        }

        internal string CheckPath => Path.Combine(BridgeDir, "checks.jsonl");
        internal string ItemsPath => Path.Combine(BridgeDir, "items.jsonl");
        internal string StatusPath => Path.Combine(BridgeDir, "status.json");
        internal string CheckedPath => Path.Combine(BridgeDir, "checked.txt");
        internal string SlotPath => Path.Combine(BridgeDir, "slot.json");
        internal string OffsetPath => Path.Combine(BridgeDir, "item_offset.txt");

        internal void LoadChecked()
        {
            try
            {
                if (!File.Exists(CheckedPath))
                    return;
                foreach (var line in File.ReadLines(CheckedPath))
                {
                    var s = line.Trim();
                    if (s.Length > 0)
                        Sent.Add(s);
                }
            }
            catch (Exception e)
            {
                Log2.LogWarning("MOONAP could not read checked.txt: " + e.Message);
            }
        }

        internal void LoadItemOffset()
        {
            try
            {
                if (File.Exists(OffsetPath))
                    long.TryParse(File.ReadAllText(OffsetPath).Trim(), out ItemOffset);
            }
            catch { }
        }

        internal void SaveItemOffset()
        {
            try { File.WriteAllText(OffsetPath, ItemOffset.ToString(CultureInfo.InvariantCulture)); } catch { }
        }

        internal void LoadSlot(bool force = false)
        {
            try
            {
                if (!File.Exists(SlotPath))
                    return;
                var write = File.GetLastWriteTimeUtc(SlotPath);
                if (!force && write == SlotWrite)
                    return;
                SlotWrite = write;
                Slot = SlotData.Parse(File.ReadAllText(SlotPath));
                Log2.LogInfo($"MOONAP slot loaded: goal={Slot.GoalSectors} grants={Slot.ItemGrants.Count} purchases={Slot.PurchaseLocations.Count} money={Slot.MoneyItems.Count}");
            }
            catch (Exception e)
            {
                Log2.LogWarning("MOONAP could not read slot.json: " + e.Message);
            }
        }

        internal void Send(string location)
        {
            if (string.IsNullOrEmpty(location) || !Sent.Add(location))
                return;
            try
            {
                var json = JsonSerializer.Serialize(new Dictionary<string, object>
                {
                    ["type"] = "check",
                    ["location"] = location,
                    ["time"] = DateTime.UtcNow.ToString("O"),
                });
                File.AppendAllText(CheckPath, json + "\n");
                File.AppendAllText(CheckedPath, location + "\n");
            }
            catch (Exception e)
            {
                Log2.LogWarning("MOONAP check write failed: " + e.Message);
            }
        }

        internal void SendGoal()
        {
            if (GoalSent)
                return;
            GoalSent = true;
            try
            {
                var json = JsonSerializer.Serialize(new Dictionary<string, object> { ["type"] = "goal" });
                File.AppendAllText(CheckPath, json + "\n");
                Log2.LogInfo("MOONAP goal reached");
            }
            catch { }
        }

        internal void WriteStatus(MoonWorld world, string player)
        {
            try
            {
                int completed = 0;
                try { completed = world.CompletedRegionCount; } catch { }
                int goal = Slot.GoalSectors;
                var json = JsonSerializer.Serialize(new Dictionary<string, object>
                {
                    ["player"] = player ?? "",
                    ["completed"] = completed,
                    ["goal"] = goal,
                    ["sectors"] = 163842,
                    ["checks_sent"] = Sent.Count,
                    ["items_applied"] = ItemsApplied,
                    ["goal_sent"] = GoalSent,
                    ["updated"] = DateTime.UtcNow.ToString("O"),
                });
                File.WriteAllText(StatusPath, json);
            }
            catch { }
        }

        internal void ApplyMoney(MoonWorld world, string player, int amount)
        {
            try
            {
                int scaled = amount * Math.Max(1, Slot.MoneyMultiplier);
                world.DevAddMoney(player, ToDecimal(scaled));
                Log2.LogInfo($"MOONAP money +{scaled} -> {player}");
            }
            catch (Exception e)
            {
                Log2.LogWarning("MOONAP money failed: " + e.Message);
            }
        }

        internal static Il2CppSystem.Decimal ToDecimal(decimal value)
        {
            return new Il2CppSystem.Decimal((double)value);
        }

        internal decimal Wallet(MoonWorld world, string player)
        {
            try { return (decimal)world.WalletDollars(player).System_IConvertible_ToDecimal(null); } catch { return 0m; }
        }

        internal void Refund(MoonWorld world, string player, decimal before)
        {
            try
            {
                var after = Wallet(world, player);
                var spent = before - after;
                if (spent > 0m)
                {
                    world.DevAddMoney(player, ToDecimal(spent));
                    Log2.LogInfo($"MOONAP refunded {spent}");
                }
            }
            catch { }
        }

        internal void ApplyItem(MoonWorld world, string player, string item)
        {
            if (string.IsNullOrEmpty(item))
                return;

            if (Slot.MoneyItems.TryGetValue(item, out var money))
            {
                ApplyMoney(world, player, money);
                ItemsApplied++;
                return;
            }

            if (!Slot.ItemGrants.TryGetValue(item, out var grant) || grant.Count < 2)
            {
                Log2.LogWarning($"MOONAP no grant for item '{item}'");
                ItemsApplied++;
                return;
            }

            var kind = grant[0];
            var id = grant[1];
            try
            {
                decimal before = Wallet(world, player);
                // Purchase APIs charge the wallet. Float the cost, then put the wallet back to where it was.
                world.DevAddMoney(player, ToDecimal(100000m));

                bool ok;
                string msg = "";
                switch (kind)
                {
                    case "tool":
                    {
                        int level = NodeLevel.TryGetValue("tool:" + id, out var l) ? l : 0;
                        ok = world.TryPurchaseTool(player, id, level, out msg);
                        if (!ok)
                            ok = world.CrewPurchase(player, MoonWorld.PurchaseKind.Tool, id, level + 1);
                        if (ok) NodeLevel["tool:" + id] = level + 1;
                        break;
                    }
                    case "tree":
                    {
                        int level = NodeLevel.TryGetValue(id, out var l) ? l : 0;
                        ok = world.TryPurchaseTreeNode(player, id, level, out msg);
                        if (!ok)
                            ok = world.CrewPurchase(player, MoonWorld.PurchaseKind.TreeNode, id, level + 1);
                        if (ok) NodeLevel[id] = level + 1;
                        break;
                    }
                    case "container":
                    {
                        int tier = ContainerTier.TryGetValue(id, out var t) ? t : 0;
                        ok = world.TryPurchaseContainer(player, id, tier, out msg);
                        if (!ok)
                            ok = world.CrewPurchase(player, MoonWorld.PurchaseKind.Container, id, tier + 1);
                        if (ok) ContainerTier[id] = tier + 1;
                        break;
                    }
                    case "vehicle":
                    {
                        int index = int.TryParse(id, out var v) ? v : 0;
                        ok = world.TryBuyVehicle(player, 0, index, out msg);
                        break;
                    }
                    default:
                        Log2.LogWarning($"MOONAP unknown grant kind '{kind}' for {item}");
                        ItemsApplied++;
                        return;
                }

                if (!ok)
                {
                    Log2.LogWarning($"MOONAP purchase path failed {item} ({kind}:{id}): {msg}; trying direct grant");
                    ok = GrantDirect(world, player, kind, id);
                }

                decimal excess = Wallet(world, player) - before;
                if (excess != 0m)
                {
                    world.DevAddMoney(player, ToDecimal(-excess));
                    Log2.LogInfo($"MOONAP wallet reconciled by {-excess}");
                }

                if (ok)
                {
                    Log2.LogInfo($"MOONAP granted {item} ({kind}:{id})");
                    if (kind == "tool" && NodeLevel.TryGetValue("tool:" + id, out var toolLevel))
                        SendPurchaseCheck("tool", id, toolLevel);
                    else if (kind == "tree" && NodeLevel.TryGetValue(id, out var treeLevel))
                        SendPurchaseCheck("tree", id, treeLevel);
                    else if (kind == "container" && ContainerTier.TryGetValue(id, out var tierLevel))
                        SendPurchaseCheck("container", id, tierLevel);
                    else if (kind == "vehicle" && int.TryParse(id, out var vehicleIndex))
                        OnVehicle(vehicleIndex);
                }
                else
                {
                    Log2.LogWarning($"MOONAP grant failed {item} ({kind}:{id})");
                }
            }
            catch (Exception e)
            {
                Log2.LogWarning($"MOONAP grant error {item}: {e.Message}");
            }
            ItemsApplied++;
        }

        internal bool GrantDirect(MoonWorld world, string player, string kind, string id)
        {
            try
            {
                var state = world.PlayerUpgradeState(player);
                if (state == null)
                    return false;
                if (kind == "tree")
                {
                    int current = state.tree.ContainsKey(id) ? state.tree.get_Item(id) : 0;
                    state.tree.set_Item(id, current + 1);
                    world.SetPlayerUpgradeState(player, state);
                    world.TreeVersion = world.TreeVersion + 1;
                    world.CommitUpgrade(player);
                    Log2.LogInfo($"MOONAP direct tree {id} -> {world.TreeLevel(player, id)}");
                    return world.TreeLevel(player, id) > current;
                }
                if (kind == "container")
                {
                    int current = state.containers.ContainsKey(id) ? state.containers.get_Item(id) : 0;
                    state.containers.set_Item(id, current + 1);
                    world.SetPlayerUpgradeState(player, state);
                    world.CommitUpgrade(player);
                    Log2.LogInfo($"MOONAP direct container {id} -> {world.ContainerTier(player, id)}");
                    return world.ContainerTier(player, id) > current;
                }
                if (kind == "tool")
                {
                    Log2.LogInfo($"MOONAP tool before level={world.ToolLevel(id, player)} has={state.tools.ContainsKey(id)}");
                    state.tools.set_Item(id, 1);
                    world.SetPlayerUpgradeState(player, state);
                    Log2.LogInfo($"MOONAP tool after set level={world.ToolLevel(id, player)} has={state.tools.ContainsKey(id)}");
                    world.CommitUpgrade(player);
                    Log2.LogInfo($"MOONAP tool after commit level={world.ToolLevel(id, player)}");
                    bool crew0 = world.CrewPurchase(player, MoonWorld.PurchaseKind.Tool, id, 0);
                    bool crew1 = world.CrewPurchase(player, MoonWorld.PurchaseKind.Tool, id, 1);
                    Log2.LogInfo($"MOONAP crew tool level0={crew0} level1={crew1} now={world.ToolLevel(id, player)}");
                    world.TryAssignTool(player, id, 0, out var assignMsg);
                    Log2.LogInfo($"MOONAP assign tool '{assignMsg}' has={state.tools.ContainsKey(id)}");
                    return state.tools.ContainsKey(id);
                }
            }
            catch (Exception e)
            {
                Log2.LogWarning($"MOONAP direct grant error {kind}:{id}: {e.Message}");
            }
            return false;
        }

        internal void DumpCatalog(MoonWorld world)
        {
            if (CatalogDumped)
                return;
            CatalogDumped = true;
            try
            {
                var catalog = world.UpgradeCatalog;
                if (catalog == null)
                    return;
                foreach (var offer in catalog.tools)
                {
                    if (offer?.tool == null)
                        continue;
                    Log2.LogInfo($"MOONAP TOOL|{offer.tool.toolId}|{offer.tool.displayName}|{offer.purchaseDollars}");
                }
            }
            catch (Exception e)
            {
                Log2.LogWarning("MOONAP catalog dump failed: " + e.Message);
            }
        }

        internal void ReadItems(MoonWorld world, string player)
        {
            try
            {
                if (!File.Exists(ItemsPath))
                    return;
                using var fs = new FileStream(ItemsPath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
                if (ItemOffset > fs.Length)
                    ItemOffset = 0;
                fs.Seek(ItemOffset, SeekOrigin.Begin);
                using var sr = new StreamReader(fs, Encoding.UTF8);
                string line;
                while ((line = sr.ReadLine()) != null)
                {
                    if (string.IsNullOrWhiteSpace(line))
                        continue;
                    try
                    {
                        using var doc = JsonDocument.Parse(line);
                        if (doc.RootElement.TryGetProperty("item", out var itemEl))
                            ApplyItem(world, player, itemEl.GetString());
                    }
                    catch (Exception e)
                    {
                        Log2.LogWarning("MOONAP bad item line: " + e.Message);
                    }
                }
                ItemOffset = fs.Position;
                SaveItemOffset();
            }
            catch (Exception e)
            {
                Log2.LogWarning("MOONAP items read failed: " + e.Message);
            }
        }

        internal void Tick(MoonWorld world)
        {
            if (world == null)
                return;
            if (UnityEngine.Time.time < NextTick)
                return;
            NextTick = UnityEngine.Time.time + 0.5f;

            string player = null;
            try { player = MoonWorld.LocalPlayer; } catch { }
            if (string.IsNullOrEmpty(player))
                return;

            LoadSlot();
            DumpCatalog(world);
            PollSectors(world);
            PollFlags(world);
            PollAchievements();

            ReadItems(world, player);

            if (!GoalSent && Slot.GoalSectors > 0)
            {
                int completed = 0;
                try { completed = world.CompletedRegionCount; } catch { }
                if (completed >= Slot.GoalSectors)
                    SendGoal();
            }

            WriteStatus(world, player);
        }

        internal void PollSectors(MoonWorld world)
        {
            try
            {
                var st = world.regionStates;
                if (st == null)
                    return;
                int len = st.Length;
                if (PrevStates == null || PrevStates.Length != len)
                {
                    PrevStates = new byte[len];
                    for (int i = 0; i < len; i++)
                        PrevStates[i] = st[i];
                    if (!InitialSectors)
                    {
                        InitialSectors = true;
                        for (int i = 0; i < len; i++)
                            if (PrevStates[i] == 2)
                                Send(SectorName(i));
                    }
                    return;
                }
                for (int i = 0; i < len; i++)
                {
                    byte now = st[i];
                    if (PrevStates[i] != 2 && now == 2)
                        Send(SectorName(i));
                    PrevStates[i] = now;
                }
            }
            catch (Exception e)
            {
                Log2.LogWarning("MOONAP sector poll failed: " + e.Message);
            }
        }

        internal static string SectorName(int index)
        {
            return $"Sector {index + 1:000000}";
        }

        internal void PollFlags(MoonWorld world)
        {
            try
            {
                var all = MoonLandmarks.All;
                if (all == null)
                    return;
                foreach (var flag in UnityEngine.Object.FindObjectsOfType<MoonLandmarkFlag>())
                {
                    if (flag == null || !flag.Raised)
                        continue;
                    int index = flag.Index;
                    if (index >= 0 && index < all.Length)
                        Send("Flag: " + all[index].name);
                }
                foreach (var site in UnityEngine.Object.FindObjectsOfType<MoonLunarSite>())
                {
                    if (site == null || !site.Raised)
                        continue;
                    int index = site.Index;
                    if (index >= 0 && index < all.Length)
                        Send("Site: " + all[index].name);
                }
            }
            catch (Exception e)
            {
                Log2.LogWarning("MOONAP landmark poll failed: " + e.Message);
            }
        }

        internal void PollAchievements()
        {
            try
            {
                var unlocked = MoonAchievements.unlocked;
                if (unlocked == null)
                    return;
                foreach (var id in unlocked)
                {
                    if (!string.IsNullOrEmpty(id) && AchSeen.Add(id))
                        Send("Achievement: " + id);
                }
            }
            catch (Exception e)
            {
                Log2.LogWarning("MOONAP achievement poll failed: " + e.Message);
            }
        }

        internal void OnPurchase(MoonWorld.PurchaseKind kind, string id, int level)
        {
            LoadSlot();
            string prefix = kind switch
            {
                MoonWorld.PurchaseKind.Tool => "tool",
                MoonWorld.PurchaseKind.Container => "container",
                MoonWorld.PurchaseKind.TreeNode => "tree",
                _ => null,
            };
            if (prefix == null || string.IsNullOrEmpty(id))
                return;
            for (int candidate = level; candidate <= level + 1; candidate++)
            {
                var key = $"{prefix}:{id}:{candidate}";
                if (Slot.PurchaseLocations.TryGetValue(key, out var location))
                {
                    Send(location);
                    return;
                }
            }
            Log2.LogInfo($"MOONAP purchase without check: {prefix}:{id}:{level}");
        }

        internal void SendPurchaseCheck(string kind, string id, int level)
        {
            LoadSlot();
            var key = $"{kind}:{id}:{level}";
            if (Slot.PurchaseLocations.TryGetValue(key, out var location))
                Send(location);
        }

        internal void OnVehicle(int vehicle)
        {
            LoadSlot();
            if (Slot.PurchaseLocations.TryGetValue($"vehicle:{vehicle}:1", out var location))
                Send(location);
        }
    }

    internal sealed class SlotData
    {
        public int GoalSectors = 500;
        public int MoneyMultiplier = 1;
        public readonly Dictionary<string, List<string>> ItemGrants = new();
        public readonly Dictionary<string, string> PurchaseLocations = new();
        public readonly Dictionary<string, int> MoneyItems = new();

        public static SlotData Parse(string text)
        {
            var data = new SlotData();
            using var doc = JsonDocument.Parse(text);
            var root = doc.RootElement;

            if (root.TryGetProperty("goal_sectors", out var goal))
                data.GoalSectors = goal.GetInt32();
            if (root.TryGetProperty("money_multiplier", out var multiplier))
                data.MoneyMultiplier = Math.Max(1, multiplier.GetInt32());

            if (root.TryGetProperty("item_grants", out var grants) && grants.ValueKind == JsonValueKind.Object)
            {
                foreach (var prop in grants.EnumerateObject())
                {
                    var list = new List<string>();
                    foreach (var v in prop.Value.EnumerateArray())
                        list.Add(v.ValueKind == JsonValueKind.String ? v.GetString() : v.GetRawText());
                    data.ItemGrants[prop.Name] = list;
                }
            }

            if (root.TryGetProperty("purchase_locations", out var purchases) && purchases.ValueKind == JsonValueKind.Object)
            {
                foreach (var prop in purchases.EnumerateObject())
                    data.PurchaseLocations[prop.Name] = prop.Value.GetString();
            }

            if (root.TryGetProperty("money_items", out var money) && money.ValueKind == JsonValueKind.Object)
            {
                foreach (var prop in money.EnumerateObject())
                    data.MoneyItems[prop.Name] = prop.Value.GetInt32();
            }

            return data;
        }
    }

    [HarmonyPatch(typeof(MoonWorld), nameof(MoonWorld.Update))]
    public static class MoonApUpdatePatch
    {
        [HarmonyPostfix]
        public static void Postfix(MoonWorld __instance)
        {
            try { MoonApPlugin.Instance?.Tick(__instance); }
            catch (Exception e) { MoonApPlugin.Log2?.LogError("MOONAP tick error: " + e); }
        }
    }

    [HarmonyPatch(typeof(MoonWorld), nameof(MoonWorld.CrewPurchase))]
    public static class MoonApPurchasePatch
    {
        [HarmonyPostfix]
        public static void Postfix(bool __result, MoonWorld.PurchaseKind kind, string id, int level)
        {
            if (__result)
                MoonApPlugin.Instance?.OnPurchase(kind, id, level);
        }
    }

    [HarmonyPatch(typeof(MoonWorld), "TryBuyVehicle")]
    public static class MoonApVehiclePatch
    {
        [HarmonyPostfix]
        public static void Postfix(bool __result, int vehicle)
        {
            if (__result)
                MoonApPlugin.Instance?.OnVehicle(vehicle);
        }
    }
}
