from __future__ import annotations

from BaseClasses import Item, ItemClassification

from . import data


class MoonSweepersItem(Item):
    game = data.GAME_NAME


def tool_name(tool_id: str, display: str) -> str:
    return f"Tool: {display}"


TOOL_ITEMS = [(f"Tool: {display}", tool_id) for tool_id, display, _ in data.TOOLS]
CONTAINER_ITEMS = [
    (f"Progressive Container: {display}", tool_id)
    for tool_id, display, _ in data.TOOLS
]
TREE_ITEMS = [
    (f"Progressive Upgrade: {title}", node_id, max_level)
    for node_id, title, max_level in data.TREE_NODES
    if not node_id.startswith("container.")
]
VEHICLE_ITEMS = [(f"Vehicle: {display}", index) for index, (_, display) in enumerate(data.VEHICLES)]


def build_item_table() -> dict[str, int]:
    table: dict[str, int] = {}
    next_id = 1

    def add(name: str) -> None:
        nonlocal next_id
        if name not in table:
            table[name] = next_id
            next_id += 1

    for name, _ in TOOL_ITEMS:
        add(name)
    for name, _ in CONTAINER_ITEMS:
        add(name)
    for name, _, _ in TREE_ITEMS:
        add(name)
    for name, _ in VEHICLE_ITEMS:
        add(name)
    for name, _, _ in data.FILLER:
        add(name)
    return table


ITEM_NAME_TO_ID = build_item_table()


def create_item(world, name: str) -> MoonSweepersItem:
    return MoonSweepersItem(name, ItemClassification.useful, ITEM_NAME_TO_ID[name], world.player)


def create_items(world) -> None:
    pool: list[MoonSweepersItem] = []

    # Toothbrush is the starting tool: pre-collect it, do not put it in the pool.
    world.multiworld.push_precollected(world.create_item("Tool: Toothbrush"))

    for name, _ in TOOL_ITEMS:
        if name == "Tool: Toothbrush":
            continue
        pool.append(world.create_item(name))
    for name, _ in CONTAINER_ITEMS:
        for _level in range(3):
            pool.append(world.create_item(name))
    for name, _node, max_level in TREE_ITEMS:
        for _level in range(max_level):
            pool.append(world.create_item(name))
    for name, _ in VEHICLE_ITEMS:
        pool.append(world.create_item(name))

    location_count = len(world.multiworld.get_unfilled_locations(world.player))
    filler_count = max(0, location_count - len(pool))
    for _ in range(filler_count):
        pool.append(world.create_item(world.get_filler_item_name()))

    world.multiworld.itempool += pool


def get_random_filler_item_name(world) -> str:
    names = [name for name, _value, _weight in data.FILLER]
    weights = [weight for _name, _value, weight in data.FILLER]
    return world.random.choices(names, weights=weights, k=1)[0]
