# AgenticADB

A token-efficient Android UI parser that converts bulky XML into minified JSON for LLM-driven automation testing.

## Goal
Empower LLM Agents to automate Android devices with zero vision cost by stripping useless XML noise and providing pre-calculated center-click coordinates.

## Features
- **Token Efficiency:** Compresses the UI hierarchy down to the bare essentials required for an LLM to take action.
- **Noise Filtering:** Discards non-actionable, invisible nodes to prevent LLM hallucination and context-bloat.
- **Coordinate Calculation:** Automatically parses the `bounds` attribute and provides explicit `center_x` and `center_y` integer keys to ensure accurate tapping.
- **Action Abstraction:** Built-in Python bindings to tap, swipe, and input text (automatically handling shell-escaping).

## Usage

You can use the provided command line tool:
```bash
# Dump the current UI hierarchy on the default device, parsing to stdout
python3 main.py

# Specify an output json file and a device, and optionally save the raw XML
python3 main.py -d emulator-5554 -o view.json --raw
```

## Structure
- `agentic_adb/parser.py`: Handles XML parsing, noise reduction, and formatting.
- `agentic_adb/adb_client.py`: Provides Python-native methods to interact with `adb`.
- `agentic_adb/models.py`: Strongly typed representations using Dataclasses.
