from __future__ import annotations

from BaseClasses import Location

from . import data


class MoonSweepersLocation(Location):
    game = data.GAME_NAME


VICTORY_NAME = "Victory"
VICTORY_ID = 999_999


def sector_name(index: int) -> str:
    """1-based display name for a 0-based sector/region id."""
    return f"Sector {index + 1:06d}"


def build_all_names() -> dict[str, int]:
    table: dict[str, int] = {}
    for i in range(data.SECTOR_COUNT):
        table[sector_name(i)] = 1 + i
    base = 300_000
    for i, name in enumerate(data.FLAGS):
        table[f"Flag: {name}"] = base + i
    base = 400_000
    for i, name in enumerate(data.SITES):
        table[f"Site: {name}"] = base + i
    base = 500_000
    for i, name in enumerate(data.ACHIEVEMENTS):
        table[f"Achievement: {name}"] = base + i
    base = 600_000
    for i, (name, _kind, _item_id, _level) in enumerate(data.SHOP):
        table[name] = base + i
    return table


ALL_LOCATION_NAMES = build_all_names()
LOCATION_NAME_TO_ID = ALL_LOCATION_NAMES


def included_sector_indices(world) -> list[int]:
    option = world.options.sector_checks.value
    if option == world.options.sector_checks.option_sample:
        step = max(1, world.options.sector_sample.value)
        return list(range(0, data.SECTOR_COUNT, step))
    return list(range(data.SECTOR_COUNT))


def included_names(world) -> list[str]:
    names: list[str] = [sector_name(i) for i in included_sector_indices(world)]
    if world.options.flag_checks:
        names.extend(f"Flag: {n}" for n in data.FLAGS)
    if world.options.site_checks:
        names.extend(f"Site: {n}" for n in data.SITES)
    if world.options.achievement_checks:
        names.extend(f"Achievement: {n}" for n in data.ACHIEVEMENTS)
    names.extend(name for name, _kind, _item_id, _level in data.SHOP)
    names.append(VICTORY_NAME)
    return names
