"""Archipelago client for Moon Sweepers.

The BepInEx plugin owns the game side and talks to this client through a small
file bridge in ``BepInEx/config/moon_ap``:

  checks.jsonl   plugin -> client  (sector / landmark / purchase checks, goal)
  items.jsonl    client -> plugin  (received items, in order)
  slot.json      client -> plugin  (slot data: goal, grants, purchase names)
  status.json    plugin -> client  (live progress, for display)

This keeps all AP protocol code in Python and the C# side dumb: it only needs
to watch game state and call the game's own purchase/pay methods.
"""
from __future__ import annotations

import argparse
import asyncio
import contextlib
import json
import os
import time
from pathlib import Path

import colorama

import Utils
from CommonClient import (CommonContext, get_base_parser, gui_enabled, handle_url_arg, logger, server_loop)
from NetUtils import ClientStatus

DEFAULT_BRIDGE = Path(r"C:\Steam\steamapps\common\Moon Sweepers\BepInEx\config\moon_ap")


class MoonContext(CommonContext):
    game = "Moon Sweepers"
    items_handling = 0b111

    def __init__(self, server_address: str | None, password: str | None, bridge: Path):
        super().__init__(server_address, password)
        self.bridge = bridge
        self.check_offset = 0
        self.items_sent = 0
        self.goal_sent = False
        self.slot_written_for: int | None = None
        self.name_to_id: dict[str, int] = {}
        self.slot_data: dict = {}
        self._read_offsets()

    # ---- bridge state -------------------------------------------------
    def _read_offsets(self) -> None:
        self.bridge.mkdir(parents=True, exist_ok=True)
        try:
            self.check_offset = int((self.bridge / "client_offset.txt").read_text().strip() or 0)
        except (OSError, ValueError):
            self.check_offset = 0
        try:
            self.items_sent = int((self.bridge / "client_items.txt").read_text().strip() or 0)
        except (OSError, ValueError):
            self.items_sent = 0

    def _write_offsets(self) -> None:
        try:
            (self.bridge / "client_offset.txt").write_text(str(self.check_offset))
            (self.bridge / "client_items.txt").write_text(str(self.items_sent))
        except OSError:
            pass

    # ---- AP connection ------------------------------------------------
    def on_package(self, cmd: str, args: dict) -> None:
        if cmd == "Connected":
            self.slot_data = args.get("slot_data") or {}
        super().on_package(cmd, args)

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def _build_name_lookup(self) -> None:
        try:
            lookup = self.location_names[self.game]
        except KeyError:
            return
        self.name_to_id = {name: loc_id for loc_id, name in lookup.items()}

    def _write_slot_data(self) -> None:
        if self.slot is None or self.slot_data is None:
            return
        if self.slot_written_for == self.slot:
            return
        payload = dict(self.slot_data)
        payload.setdefault("goal_sectors", 500)
        payload["player"] = self.auth
        payload["slot"] = self.slot
        try:
            (self.bridge / "slot.json").write_text(json.dumps(payload))
            self.slot_written_for = self.slot
            logger.info(f"Wrote slot data ({payload.get('goal_sectors')} sectors goal) to {self.bridge}")
        except OSError as exc:
            logger.warning(f"Could not write slot.json: {exc}")

    # ---- checks -------------------------------------------------------
    async def _poll_checks(self) -> None:
        path = self.bridge / "checks.jsonl"
        if not path.exists():
            return
        try:
            with path.open("r", encoding="utf-8") as handle:
                handle.seek(self.check_offset)
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if msg.get("type") == "goal":
                        if not self.goal_sent:
                            self.goal_sent = True
                            await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                            logger.info("Goal sent to the server.")
                        continue
                    name = msg.get("location")
                    if not name:
                        continue
                    loc_id = self.name_to_id.get(name)
                    if loc_id is None:
                        logger.debug(f"Unknown location in bridge: {name}")
                        continue
                    await self.check_locations([loc_id])
                self.check_offset = handle.tell()
        except OSError:
            return
        self._write_offsets()

    # ---- items --------------------------------------------------------
    async def _push_items(self) -> None:
        if not self.items_received:
            return
        if self.items_sent > len(self.items_received):
            # New session with fewer items than before (new seed): restart.
            self.items_sent = 0
        if self.items_sent == len(self.items_received):
            return

        path = self.bridge / "items.jsonl"
        new_lines = []
        for index in range(self.items_sent, len(self.items_received)):
            item = self.items_received[index]
            name = self.item_names.lookup_in_slot(item.item, item.player)
            new_lines.append(json.dumps({"index": index, "item": name, "player": item.player}))
        if not new_lines:
            return
        try:
            with path.open("a", encoding="utf-8") as handle:
                handle.write("\n".join(new_lines) + "\n")
        except OSError as exc:
            logger.warning(f"Could not write items.jsonl: {exc}")
            return
        self.items_sent = len(self.items_received)
        self._write_offsets()
        logger.info(f"Queued {len(new_lines)} item(s) for the game.")

    # ---- loop ---------------------------------------------------------
    async def bridge_loop(self) -> None:
        while not self.exit_event.is_set():
            try:
                if self.slot is not None:
                    if not self.name_to_id:
                        self._build_name_lookup()
                    self._write_slot_data()
                    await self._poll_checks()
                    await self._push_items()
            except Exception as exc:  # keep the bridge alive
                logger.exception(f"Moon bridge error: {exc}")
            await asyncio.sleep(0.5)


async def _main(args: argparse.Namespace) -> None:
    bridge = Path(args.bridge) if args.bridge else DEFAULT_BRIDGE
    ctx = MoonContext(args.connect, args.password, bridge)
    ctx.auth = args.name
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
    bridge_task = asyncio.create_task(ctx.bridge_loop(), name="Moon bridge loop")
    if gui_enabled and not getattr(args, "nogui", False):
        ctx.run_gui()
    ctx.run_cli()
    try:
        await ctx.exit_event.wait()
    finally:
        bridge_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await bridge_task
        await ctx.shutdown()


def launch(*launch_args: str) -> None:
    parser = get_base_parser(description="Moon Sweepers Archipelago Client")
    parser.add_argument("--name", default=None, help="Slot name to connect as.")
    parser.add_argument("--bridge", default=None, help="Path to BepInEx/config/moon_ap.")
    parser.add_argument("url", nargs="?", help="archipelago:// connection URL")
    args = handle_url_arg(parser.parse_args(launch_args or None), parser)
    Utils.init_logging("MoonSweepersClient", exception_logger="Client")
    colorama.just_fix_windows_console()
    try:
        asyncio.run(_main(args))
    finally:
        colorama.deinit()


if __name__ == "__main__":
    launch()
