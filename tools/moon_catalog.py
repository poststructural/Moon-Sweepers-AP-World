import json, struct, os, re

root = r"C:\Users\unowi\Documents\APWorldMaker\MoonSweepersAP\research"
grid = os.path.join(root, "textassets")

def grid_count(name):
    b = open(os.path.join(grid, name), "rb").read()
    magic, level, count, stride = struct.unpack_from("<4sIII", b, 0)
    return {"level": level, "count": count, "bytes": len(b)}

sites = json.load(open(os.path.join(grid, "sites.txt"), encoding="utf-8"))
flags = json.load(open(os.path.join(grid, "flags.txt"), encoding="utf-8"))
lits = open(os.path.join(root, "moon_literals.txt"), encoding="utf-8").read().splitlines()
achievements = sorted({s for s in lits if re.fullmatch(r"ACH_[A-Z0-9_]+", s)})

catalog = {
    "game": "Moon Sweepers",
    "build": {"unity": "6000.6.0f1", "il2cpp_metadata": 108, "namespace": "MoonCleaners"},
    "counts": {
        "sectors": grid_count("RegionGrid_L7.bin")["count"],
        "regions_l6": grid_count("RegionGrid_L6.bin")["count"],
        "sites": len(sites["sites"]),
        "flags": len(flags["flags"]),
        "achievements": len(achievements),
    },
    "region_grid": {f"L{i}": grid_count(f"RegionGrid_L{i}.bin") for i in range(8)},
    "tools": [
        "Toothbrush", "Hand brush", "Nail brush", "Detail brush", "Angled edge brush",
        "Household broom", "Wide broom", "Extra wide broom", "Telescopic brush",
        "Rotary brush", "Hand vacuum", "Backpack vacuum",
    ],
    "vehicles": ["Push sweeper", "Ride-on sweeper", "Crew transport van", "Lunar sweeper", "Mega vacuum rover"],
    "vehicle_upgrades": ["Speed", "Hopper", "Boost", "Cruise control", "Suction", "Lights"],
    "achievements": achievements,
    "sites": [
        {"code": s["code"], "name": s["name"], "kind": s["kind"], "nation": s["nation"]}
        for s in sites["sites"]
    ],
    "flags": [{"code": f["code"], "name": f["name"]} for f in flags["flags"]],
}
out = r"C:\Users\unowi\Documents\APWorldMaker\MoonSweepersAP\research\moon_catalog.json"
json.dump(catalog, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("wrote", out)
print(json.dumps(catalog["counts"], indent=1))
