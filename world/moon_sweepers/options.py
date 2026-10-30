from dataclasses import dataclass

from Options import Choice, DefaultOnToggle, OptionGroup, PerGameCommonOptions, Range


class SectorChecks(Choice):
    """How many of the Moon's 163,842 sectors become checks.

    all: every sector (the max seed).
    sample: every Nth sector, set by sector_sample."""

    display_name = "Sector Checks"
    option_all = 0
    option_sample = 1
    default = 0


class SectorSample(Range):
    """When sector_checks is sample, include every Nth sector."""

    display_name = "Sector Sample Step"
    range_start = 1
    range_end = 1000
    default = 10


class FlagChecks(DefaultOnToggle):
    """Raising one of the 195 country flags is a check."""

    display_name = "Flag Checks"


class SiteChecks(DefaultOnToggle):
    """Surveying one of the 26 lunar lander/rover/crash sites is a check."""

    display_name = "Lunar Site Checks"


class AchievementChecks(DefaultOnToggle):
    """Unlocking one of the 33 Steam achievements is a check."""

    display_name = "Achievement Checks"


class GoalSectors(Range):
    """Clean this many sectors to finish the seed."""

    display_name = "Goal: Sectors Cleaned"
    range_start = 1
    range_end = 163842
    default = 500


OPTION_GROUPS = [
    OptionGroup("Checks", [SectorChecks, SectorSample, FlagChecks, SiteChecks, AchievementChecks]),
    OptionGroup("Goal", [GoalSectors]),
]


@dataclass
class MoonSweepersOptions(PerGameCommonOptions):
    sector_checks: SectorChecks
    sector_sample: SectorSample
    flag_checks: FlagChecks
    site_checks: SiteChecks
    achievement_checks: AchievementChecks
    goal_sectors: GoalSectors
