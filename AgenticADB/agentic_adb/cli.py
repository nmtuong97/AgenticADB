import argparse
import sys
import json
import os
from agentic_adb.client import ADBClient, IDBClient
from agentic_adb.parser import ADBParser, IDBParser
from agentic_adb.service import UIQueryService, UIActionService
from agentic_adb.device_utils import resolve_device
from agentic_adb.exceptions import CommandError, ParseError, DeviceNotFoundError

def run_cli(args_list: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="AgenticADB: Token-efficient Android and iOS UI parser for LLM-driven automation.")

    # Global arguments
    parser.add_argument("-d", "--device", help="Target device ID")
    parser.add_argument("--os", choices=["android", "ios"], help="Target OS override (android or ios)")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # Command: dump
    dump_parser = subparsers.add_parser("dump", help="Outputs the minified JSON")
    dump_parser.add_argument("-o", "--output", help="Path to save the JSON file (default to stdout)")
    dump_parser.add_argument("--raw", action="store_true", help="Save the raw output alongside the JSON or to raw_dump if stdout")

    # Command: tap
    tap_parser = subparsers.add_parser("tap", help="Tap on a coordinate")
    tap_parser.add_argument("--x", type=int, required=True, help="X coordinate")
    tap_parser.add_argument("--y", type=int, required=True, help="Y coordinate")

    # Command: swipe
    swipe_parser = subparsers.add_parser("swipe", help="Swipe from one coordinate to another")
    swipe_parser.add_argument("--x1", type=int, required=True, help="Start X coordinate")
    swipe_parser.add_argument("--y1", type=int, required=True, help="Start Y coordinate")
    swipe_parser.add_argument("--x2", type=int, required=True, help="End X coordinate")
    swipe_parser.add_argument("--y2", type=int, required=True, help="End Y coordinate")
    swipe_parser.add_argument("--duration", type=int, default=500, help="Duration in ms (default 500)")

    # Command: input
    input_parser = subparsers.add_parser("input", help="Input text")
    input_parser.add_argument("--text", type=str, required=True, help="Text to input")

    # Command: long_press
    long_press_parser = subparsers.add_parser("long_press", help="Long press on a coordinate")
    long_press_parser.add_argument("--x", type=int, required=True, help="X coordinate")
    long_press_parser.add_argument("--y", type=int, required=True, help="Y coordinate")
    long_press_parser.add_argument("--duration", type=int, default=1000, help="Duration in ms (default 1000)")

    # Command: press
    press_parser = subparsers.add_parser("press", help="Press a system key")
    press_parser.add_argument("--key", type=str, required=True, help="Keycode or key name (e.g., home, back, enter)")

    # Command: launch
    launch_parser = subparsers.add_parser("launch", help="Launch an application by bundle ID")
    launch_parser.add_argument("--bundle_id", type=str, required=True, help="Bundle ID or package name")

    # Command: kill
    kill_parser = subparsers.add_parser("kill", help="Kill an application by bundle ID")
    kill_parser.add_argument("--bundle_id", type=str, required=True, help="Bundle ID or package name")

    args = parser.parse_args(args_list)

    # Resolve device via Smart Routing
    try:
        resolved_device_id, os_type = resolve_device(args.device, args.os)
    except DeviceNotFoundError as e:
        sys.stderr.write(f"Device routing error: {e}\n")
        sys.exit(1)
        return

    if os_type == "android":
        client = ADBClient(device_id=resolved_device_id)
        ui_parser = ADBParser()
    else:
        client = IDBClient(device_id=resolved_device_id)
        ui_parser = IDBParser()

    # Route based on command
    if args.command == "dump":
        query_service = UIQueryService(client=client, parser=ui_parser)
        try:
            raw_content = query_service.get_raw_ui()
        except CommandError as e:
            sys.stderr.write(f"Error communicating with device: {e}\n")
            sys.exit(1)
            return

        if args.raw:
            ext = "xml" if os_type == "android" else "json"
            if args.output:
                base, _ = os.path.splitext(args.output)
                raw_path = f"{base}_raw.{ext}"
            else:
                raw_path = f"raw_dump.{ext}"

            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(raw_content)

        try:
            ui_elements = query_service.parse_raw(raw_content)
        except ParseError as e:
            sys.stderr.write(f"Error parsing UI elements: {e}\n")
            sys.exit(1)
            return

        json_data = [element.to_dict() for element in ui_elements]
        json_str = json.dumps(json_data, indent=2)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_str)
        else:
            print(json_str)

    else:
        # It's an action command
        action_service = UIActionService(client=client)
        try:
            if args.command == "tap":
                action_service.tap(args.x, args.y)
            elif args.command == "swipe":
                action_service.swipe(args.x1, args.y1, args.x2, args.y2, args.duration)
            elif args.command == "input":
                action_service.input_text(args.text)
            elif args.command == "long_press":
                action_service.long_press(args.x, args.y, args.duration)
            elif args.command == "press":
                action_service.press_key(args.key)
            elif args.command == "launch":
                action_service.launch_app(args.bundle_id)
            elif args.command == "kill":
                action_service.kill_app(args.bundle_id)
        except CommandError as e:
            sys.stderr.write(f"Error executing {args.command}: {e}\n")
            sys.exit(1)
            return

def main() -> None:
    run_cli()

if __name__ == "__main__":
    main()
