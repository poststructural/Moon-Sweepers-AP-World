import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cat = json.loads((root / "research" / "moon_catalog.json").read_text(encoding="utf-8"))
out = root / "world" / "moon_sweepers" / "data.py"
out.parent.mkdir(parents=True, exist_ok=True)

flags = [f["name"] for f in cat["flags"]]
sites = [s["name"] for s in cat["sites"]]
achievements = cat["achievements"]

tools = [
    ("toothbrush", "Toothbrush", 1),
    ("nailbrush", "Nail Brush", 1),
    ("hand_brush", "Hand Brush", 1),
    ("household_broom", "Household Broom", 1),
    ("wide_broom", "Wide Broom", 1),
    ("extra_wide_broom", "Extra Wide Broom", 1),
]

tree = [
    ("core", "Collector Uplink", 1),
    ("container.toothbrush", "Toothbrush Container", 3),
    ("container.nailbrush", "Nail Brush Container", 3),
    ("container.hand_brush", "Hand Brush Container", 3),
    ("container.household_broom", "Household Broom Container", 3),
    ("container.wide_broom", "Wide Broom Container", 3),
    ("container.extra_wide_broom", "Extra Wide Broom Container", 3),
    ("clean.compactor", "Dust Compactor", 3),
    ("clean.autopack", "Auto-Packer", 1),
    ("clean.width", "Wide Heads", 3),
    ("clean.depth", "Deep Heads", 2),
    ("clean.reach", "Long Reach", 2),
    ("clean.surge", "Surge Heads", 1),
    ("suit.stride", "Servo Stride", 3),
    ("suit.jump", "Lunar Leap", 2),
    ("suit.exo", "Exo Frame", 1),
    ("logi.transfer", "Rapid Transfer", 3),
    ("logi.tether", "Capsule Tether", 2),
    ("logi.throw", "Throw Assist", 2),
    ("logi.express", "Express Dock", 1),
    ("eco.payout", "Market Contracts", 3),
    ("eco.discount", "Supplier Network", 2),
    ("eco.bounty", "Region Bounty", 2),
    ("eco.exchange", "Lunar Exchange", 1),
]

vehicles = [
    ("push_sweeper", "Push Sweeper"),
    ("ride_on_sweeper", "Ride-On Sweeper"),
    ("crew_transport_van", "Crew Transport Van"),
    ("lunar_sweeper", "Lunar Sweeper"),
    ("mega_vacuum_rover", "Mega Vacuum Rover"),
]

shop = []
for tool_id, display, _ in tools:
    if tool_id != "toothbrush":
        shop.append((f"Buy Tool: {display}", "tool", tool_id, 1))
for tool_id, display, _ in tools:
    for tier in range(1, 4):
        shop.append((f"Buy Container: {display} {tier}", "container", tool_id, tier))
for node_id, title, max_level in tree:
    if node_id.startswith("container."):
        continue
    for level in range(1, max_level + 1):
        shop.append((f"Buy Upgrade: {title} {level}", "tree", node_id, level))
for index, (vehicle_id, display) in enumerate(vehicles):
    shop.append((f"Buy Vehicle: {display}", "vehicle", str(index), 1))


def py_list(name, values):
    lines = [f"{name} = ["]
    for v in values:
        lines.append(f"    {v!r},")
    lines.append("]")
    return "\n".join(lines)

parts = [
    '"""Static data extracted from the Moon Sweepers build (v1.0.5, Unity 6000.6 IL2CPP v108)."""',
    "",
    'GAME_NAME = "Moon Sweepers"',
    "",
    "SECTOR_COUNT = 163842",
    "# 12 sectors are already empty at world start (state 2); they are included so the",
    "# location list matches the game's own \"There are 163,842 sectors\" text.",
    "EMPTY_SECTORS = 12",
    "",
    py_list("FLAGS", flags),
    "",
    py_list("SITES", sites),
    "",
    py_list("ACHIEVEMENTS", achievements),
    "",
    py_list("TOOLS", tools),
    "",
    py_list("TREE_NODES", tree),
    "",
    py_list("VEHICLES", vehicles),
    "",
    py_list("SHOP", shop),
    "",
    "FILLER = [",
    '    ("$50", 50, 30),',
    '    ("$100", 100, 25),',
    '    ("$250", 250, 20),',
    '    ("$500", 500, 12),',
    '    ("$1,000", 1000, 8),',
    '    ("$2,500", 2500, 5),',
    "]",
    "",
]
out.write_text("\n".join(parts), encoding="utf-8")
print("wrote", out, "flags", len(flags), "sites", len(sites), "ach", len(achievements))
