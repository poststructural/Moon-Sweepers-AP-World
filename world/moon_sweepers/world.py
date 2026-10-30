from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

from BaseClasses import ItemClassification, Region
from worlds.AutoWorld import World

from . import data, items, locations, web_world
from . import options as moon_options


class MoonSweepersWorld(World):
    """Clean the Moon. All of it.

    Moon Sweepers splits the Moon into 163,842 hexagonal sectors. Every sector is a check, and money, tools,
    upgrades and vehicles are shuffled across the multiworld."""

    game = data.GAME_NAME
    web = web_world.MoonSweepersWebWorld()
    options_dataclass = moon_options.MoonSweepersOptions
    options: moon_options.MoonSweepersOptions
    origin_region_name = "Moon"

    item_name_to_id: ClassVar[dict[str, int]] = items.ITEM_NAME_TO_ID
    location_name_to_id: ClassVar[dict[str, int]] = locations.LOCATION_NAME_TO_ID
    item_name_groups = {
        "Tools": {name for name, _ in items.TOOL_ITEMS},
        "Containers": {name for name, _ in items.CONTAINER_ITEMS},
        "Upgrades": {name for name, _, _ in items.TREE_ITEMS},
        "Vehicles": {name for name, _ in items.VEHICLE_ITEMS},
        "Money": {name for name, _, _ in data.FILLER},
    }

    def create_regions(self) -> None:
        moon = Region("Moon", self.player, self.multiworld)
        names = locations.included_names(self)
        address = {name: (None if name == locations.VICTORY_NAME else self.location_name_to_id[name]) for name in names}
        moon.add_locations(address, locations.MoonSweepersLocation)
        self.multiworld.regions.append(moon)

        victory = self.multiworld.get_location(locations.VICTORY_NAME, self.player)
        victory.place_locked_item(items.MoonSweepersItem("Victory", ItemClassification.progression, None, self.player))

    def create_item(self, name: str) -> items.MoonSweepersItem:
        return items.create_item(self, name)

    def create_items(self) -> None:
        items.create_items(self)

    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    def set_rules(self) -> None:
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)

    def fill_slot_data(self) -> Mapping[str, Any]:
        grants: dict[str, list] = {}
        for name, tool_id in items.TOOL_ITEMS:
            grants[name] = ["tool", tool_id]
        for name, tool_id in items.CONTAINER_ITEMS:
            grants[name] = ["tree", f"container.{tool_id}"]
        for name, node_id, _max_level in items.TREE_ITEMS:
            grants[name] = ["tree", node_id]
        for name, index in items.VEHICLE_ITEMS:
            grants[name] = ["vehicle", index]

        return {
            "slot_data_version": 1,
            "sector_count": data.SECTOR_COUNT,
            "goal_sectors": self.options.goal_sectors.value,
            "money_multiplier": self.options.money_multiplier.value,
            "sector_checks": self.options.sector_checks.current_key,
            "sector_sample": self.options.sector_sample.value,
            "flag_checks": bool(self.options.flag_checks),
            "site_checks": bool(self.options.site_checks),
            "achievement_checks": bool(self.options.achievement_checks),
            "victory_location": locations.VICTORY_NAME,
            "purchase_locations": {f"{kind}:{item_id}:{level}": name
                                   for name, kind, item_id, level in data.SHOP},
            "item_grants": grants,
            "money_items": {name: value for name, value, _weight in data.FILLER},
            "flags": list(data.FLAGS) if self.options.flag_checks else [],
            "sites": list(data.SITES) if self.options.site_checks else [],
            "achievements": list(data.ACHIEVEMENTS) if self.options.achievement_checks else [],
        }
