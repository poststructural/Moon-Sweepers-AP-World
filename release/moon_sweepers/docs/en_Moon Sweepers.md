# Moon Sweepers

Clean the Moon. All of it.

Moon Sweepers divides the Moon into **163,842 hexagonal sectors**. Every sector is a check, and the game pays a
bonus for each one. Country flags, lunar landing sites, achievements and shop purchases are checks too, and money,
tools, containers, upgrade-tree nodes and vehicles are shuffled across the multiworld.

The maximum seed is **164,159 locations**:

| Source | Count |
|---|---:|
| Sectors | 163,842 |
| Country flags | 195 |
| Lunar sites | 26 |
| Achievements | 33 |
| Shop purchases | 63 |

## Items

- **Money** — $50 to $2,500 per item, paid into the shared crew wallet.
- **Tools** — hand brush, nail brush, household broom, wide broom, extra wide broom.
- **Progressive containers** — three tiers per tool.
- **Progressive upgrades** — the 24-node upgrade tree (cleaning, suit, logistics, economy).
- **Vehicles** — push sweeper, ride-on sweeper, crew transport van, lunar sweeper, mega vacuum rover.

## Goal

Clean the configured number of sectors (default 500). For a normal playable seed use `sector_checks: sample`; for
the record-setting seed use `sector_checks: all`.

`money_multiplier` scales every money item (x1 to x100) for faster early upgrades.

## Setup

See [the setup guide](setup_en.md).
