using System;
using System.Collections.Generic;
using System.Text;
using BepInEx;
using BepInEx.Logging;
using BepInEx.Unity.IL2CPP;
using HarmonyLib;
using MoonCleaners;
using UnityEngine;

namespace MoonSweepers.Probe
{
    [BepInPlugin("moon.ap.probe", "Moon Sweepers AP Probe", "0.1.0")]
    public class ProbePlugin : BasePlugin
    {
        internal static ManualLogSource Log2;

        public override void Load()
        {
            Log2 = Log;
            Log.LogInfo("MOONAP probe 0.1 loaded");
            Harmony.CreateAndPatchAll(typeof(MoonWorldUpdatePatch));
        }
    }

    [HarmonyPatch(typeof(MoonWorld), nameof(MoonWorld.Update))]
    public static class MoonWorldUpdatePatch
    {
        private static bool dumped;
        private static float nextLog;

        [HarmonyPostfix]
        public static void Postfix(MoonWorld __instance)
        {
            if (__instance == null)
                return;

            float now = Time.time;
            if (now < nextLog)
                return;
            nextLog = now + 5f;

            try
            {
                var regions = __instance.Regions;
                int stateLen = -1, bankLen = -1, initialLen = -1, remainingLen = -1;
                try { stateLen = __instance.regionStates?.Length ?? -1; } catch { }
                try { bankLen = __instance.bankRegionStates?.Length ?? -1; } catch { }
                try { initialLen = __instance.regionInitial?.Length ?? -1; } catch { }
                try { remainingLen = __instance.regionRemaining?.Length ?? -1; } catch { }

                string wallet = "?";
                try { wallet = __instance.wallets?.Balance.ToString() ?? "null"; } catch (Exception e) { wallet = "err:" + e.GetType().Name; }

                ProbePlugin.Log2.LogInfo(
                    $"MOONAP regions={regions?.Count ?? -1} level={regions?.Level ?? -1} even={regions?.Even} " +
                    $"states={stateLen} bank={bankLen} initial={initialLen} remaining={remainingLen} " +
                    $"completed={__instance.CompletedRegionCount} touched={__instance.TouchedRegionCount} " +
                    $"empty={__instance.EmptyRegionCount} wallet={wallet}");

                if (stateLen > 0)
                {
                    var st = __instance.regionStates;
                    var hist = new int[8];
                    int other = 0;
                    for (int i = 0; i < st.Length; i++)
                    {
                        byte v = st[i];
                        if (v < 8) hist[v]++;
                        else other++;
                    }
                    var sb = new StringBuilder();
                    for (int i = 0; i < hist.Length; i++)
                    {
                        if (hist[i] != 0)
                            sb.Append(i).Append('=').Append(hist[i]).Append(' ');
                    }
                    sb.Append("other=").Append(other);
                    ProbePlugin.Log2.LogInfo("MOONAP state histogram " + sb);
                }

                if (!dumped)
                {
                    dumped = true;
                    DumpTree();
                }
            }
            catch (Exception e)
            {
                ProbePlugin.Log2.LogError("MOONAP probe error: " + e);
            }
        }

        private static void DumpTree()
        {
            try
            {
                var nodes = MoonUpgradeTree.Build();
                ProbePlugin.Log2.LogInfo($"MOONAP upgrade nodes={nodes.Length}");
                var seen = new HashSet<string>();
                foreach (var n in nodes)
                {
                    if (n == null || !seen.Add(n.id))
                        continue;
                    var prices = new StringBuilder();
                    try
                    {
                        var p = n.prices;
                        if (p != null)
                        {
                            for (int i = 0; i < p.Length && i < 6; i++)
                            {
                                if (i > 0) prices.Append(',');
                                prices.Append(p[i]);
                            }
                        }
                    }
                    catch { }
                    ProbePlugin.Log2.LogInfo(
                        $"MOONAP NODE|{n.id}|{n.title}|{n.summary}|branch={n.branch}|max={n.maxLevel}|prices={prices}|tool={n.tool}|capstone={n.capstone}");
                }
            }
            catch (Exception e)
            {
                ProbePlugin.Log2.LogError("MOONAP tree dump failed: " + e);
            }
        }
    }
}
