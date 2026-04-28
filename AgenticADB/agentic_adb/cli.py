import argparse
import sys
import json
import os
from agentic_adb.client import ADBClient, IDBClient
from agentic_adb.parser import ADBParser, IDBParser
from agentic_adb.service import UIQueryService, UIActionService
from agentic_adb.exceptions import CommandError, ParseError

def run_cli(args_list: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="AgenticADB: Token-efficient Android/iOS UI parser and automation CLI.")

    # Global arguments
    parser.add_argument("--os", choices=["android", "ios"], default="android", help="Target OS (android or ios)")
    parser.add_argument("-d", "--device", help="Target device ID")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # dump command (default behavior previously)
    dump_parser = subparsers.add_parser("dump", help="Dump the UI hierarchy to minified JSON")
    dump_parser.add_argument("-o", "--output", help="Path to save the JSON file (default to stdout)")
    dump_parser.add_argument("--raw", action="store_true", help="Save the raw output alongside the JSON or to raw_dump if stdout")

    # tap command
    tap_parser = subparsers.add_parser("tap", help="Tap at coordinate (x, y)")
    tap_parser.add_argument("--x", type=int, required=True, help="X coordinate")
    tap_parser.add_argument("--y", type=int, required=True, help="Y coordinate")

    # swipe command
    swipe_parser = subparsers.add_parser("swipe", help="Swipe from (x1, y1) to (x2, y2)")
    swipe_parser.add_argument("--x1", type=int, required=True, help="Start X coordinate")
    swipe_parser.add_argument("--y1", type=int, required=True, help="Start Y coordinate")
    swipe_parser.add_argument("--x2", type=int, required=True, help="End X coordinate")
    swipe_parser.add_argument("--y2", type=int, required=True, help="End Y coordinate")
    swipe_parser.add_argument("--duration", type=int, default=500, help="Duration in ms (default: 500)")

    # input command
    input_parser = subparsers.add_parser("input", help="Input text into focused field")
    input_parser.add_argument("text", type=str, help="Text to input")

    # long_press command
    long_press_parser = subparsers.add_parser("long_press", help="Long press at coordinate (x, y)")
    long_press_parser.add_argument("--x", type=int, required=True, help="X coordinate")
    long_press_parser.add_argument("--y", type=int, required=True, help="Y coordinate")
    long_press_parser.add_argument("--duration", type=int, default=1000, help="Duration in ms (default: 1000)")

    # press command
    press_parser = subparsers.add_parser("press", help="Press system key (e.g., home, back)")
    press_parser.add_argument("key", type=str, help="System key name")

    # launch command
    launch_parser = subparsers.add_parser("launch", help="Launch application by bundle ID")
    launch_parser.add_argument("bundle", type=str, help="Bundle ID / Package name")

    # kill command
    kill_parser = subparsers.add_parser("kill", help="Kill application by bundle ID")
    kill_parser.add_argument("bundle", type=str, help="Bundle ID / Package name")

    # If no arguments provided, print help
    if not args_list and len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args(args_list)

    # Setup clients
    if args.os == "android":
        client = ADBClient(device_id=args.device)
        ui_parser = ADBParser()
    else:
        client = IDBClient(device_id=args.device)
        ui_parser = IDBParser()

    # Default to dump if command is not specified (for backwards compatibility if possible, though subparsers usually require command)
    command = args.command if args.command else "dump"

    try:
        if command == "dump":
            query_service = UIQueryService(client=client, parser=ui_parser)
            raw_content = query_service.get_raw_ui()

            if hasattr(args, 'raw') and args.raw:
                ext = "xml" if args.os == "android" else "json"
                if hasattr(args, 'output') and args.output:
                    base, _ = os.path.splitext(args.output)
                    raw_path = f"{base}_raw.{ext}"
                else:
                    raw_path = f"raw_dump.{ext}"

                with open(raw_path, "w", encoding="utf-8") as f:
                    f.write(raw_content)

            ui_elements = query_service.parse_raw(raw_content)
            json_data = [element.to_dict() for element in ui_elements]
            json_str = json.dumps(json_data, indent=2)

            if hasattr(args, 'output') and args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(json_str)
            else:
                print(json_str)

        elif command == "tap":
            action_service = UIActionService(client=client)
            action_service.tap(args.x, args.y)
        elif command == "swipe":
            action_service = UIActionService(client=client)
            action_service.swipe(args.x1, args.y1, args.x2, args.y2, args.duration)
        elif command == "input":
            action_service = UIActionService(client=client)
            action_service.input_text(args.text)
        elif command == "long_press":
            action_service = UIActionService(client=client)
            action_service.long_press(args.x, args.y, args.duration)
        elif command == "press":
            action_service = UIActionService(client=client)
            action_service.press_keycode(args.key)
        elif command == "launch":
            action_service = UIActionService(client=client)
            action_service.launch_app(args.bundle)
        elif command == "kill":
            action_service = UIActionService(client=client)
            action_service.kill_app(args.bundle)

    except CommandError as e:
        sys.stderr.write(f"Error communicating with device: {e}\n")
        sys.exit(1)
    except ParseError as e:
        sys.stderr.write(f"Error parsing UI elements: {e}\n")
        sys.exit(1)

def main() -> None:
    run_cli()

if __name__ == "__main__":
    main()
