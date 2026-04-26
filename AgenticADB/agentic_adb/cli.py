import argparse
import sys
import json
import os
from agentic_adb.client import ADBClient, IDBClient
from agentic_adb.parser import ADBParser, IDBParser
from agentic_adb.service import UIQueryService

def run_cli(args_list: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="AgenticADB: Token-efficient Android UI parser for LLM-driven automation.")
    parser.add_argument("--os", choices=["android", "ios"], default="android", help="Target OS (android or ios)")
    parser.add_argument("-d", "--device", help="Target device ID")
    parser.add_argument("-o", "--output", help="Path to save the JSON file (default to stdout)")
    parser.add_argument("--raw", action="store_true", help="Save the raw output alongside the JSON or to raw_dump if stdout")

    args = parser.parse_args(args_list)

    if args.os == "android":
        client = ADBClient(device_id=args.device)
        ui_parser = ADBParser()
    else:
        client = IDBClient(device_id=args.device)
        ui_parser = IDBParser()

    query_service = UIQueryService(client=client, parser=ui_parser)

    from agentic_adb.exceptions import CommandError, ParseError

    try:
        raw_content = query_service.get_raw_ui()
    except CommandError as e:
        sys.stderr.write(f"Error communicating with device: {e}\n")
        sys.exit(1)
        return

    if args.raw:
        ext = "xml" if args.os == "android" else "json"
        if args.output:
            # Save raw next to the output json file
            base, _ = os.path.splitext(args.output)
            raw_path = f"{base}_raw.{ext}"
        else:
            # No output, so we save to default raw_dump
            raw_path = f"raw_dump.{ext}"

        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(raw_content)
        # Avoid printing to stdout to keep it clean for JSON

    # Parse and minify the output to JSON using the query service
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
        # Print JSON strictly to stdout
        print(json_str)

def main() -> None:
    run_cli()

if __name__ == "__main__":
    main()
