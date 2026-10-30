from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld

from . import options as moon_options


class MoonSweepersWebWorld(WebWorld):
    theme = "grass"
    option_groups = moon_options.OPTION_GROUPS
    tutorials = [
        Tutorial(
            "Multiworld Setup Guide",
            "A guide to setting up Moon Sweepers for Archipelago.",
            "English",
            "setup_en.md",
            "setup/en",
            ["Jerrod"],
        )
    ]
