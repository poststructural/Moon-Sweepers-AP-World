from worlds.LauncherComponents import Component, Type, components, launch as launch_component

from .world import MoonSweepersWorld as MoonSweepersWorld


def launch_client(*args: str) -> None:
    from .client import launch
    launch_component(launch, name="MoonSweepersClient", args=args)


components.append(Component("Moon Sweepers Client", func=launch_client, component_type=Type.CLIENT,
                            game_name="Moon Sweepers", supports_uri=True,
                            description="Connects Moon Sweepers (BepInEx plugin bridge) to a multiworld."))
