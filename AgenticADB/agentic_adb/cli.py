import argparse
import sys
import json
import os
from agentic_adb.adb_client import ADBClient
from agentic_adb.parser import parse_xml

def main() -> None:
    parser = argparse.ArgumentParser(description="AgenticADB: Token-efficient Android UI parser for LLM-driven automation.")
    parser.add_argument("-d", "--device", help="Target device ID")
    parser.add_argument("-o", "--output", help="Path to save the JSON file (default to stdout)")
    parser.add_argument("--raw", action="store_true", help="Save the raw XML alongside the JSON or to raw_dump.xml if stdout")

    args = parser.parse_args()

    client = ADBClient(device_id=args.device)

    try:
        xml_content = client.dump()
    except Exception as e:
        sys.stderr.write(f"Error communicating with ADB: {e}\n")
        sys.exit(1)

    if args.raw:
        if args.output:
            # Save raw next to the output json file
            base, _ = os.path.splitext(args.output)
            raw_path = f"{base}_raw.xml"
        else:
            # No output, so we save to default raw_dump.xml
            raw_path = "raw_dump.xml"

        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        # Avoid printing to stdout to keep it clean for JSON

    # Parse and minify the XML to JSON
    ui_elements = parse_xml(xml_content)
    json_data = [element.to_dict() for element in ui_elements]
    json_str = json.dumps(json_data, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
    else:
        # Print JSON strictly to stdout
        print(json_str)

if __name__ == "__main__":
    main()
