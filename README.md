# AgenticADB

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)

**A token-efficient Android & iOS UI bridge for LLM Agents**

## Prerequisites

Before using AgenticADB, you must have the appropriate command-line tools installed and globally accessible in your system's PATH.

- **Android:** Install Android Debug Bridge (`adb`).
  - macOS: `brew install android-platform-tools`
  - Or via Android Studio SDK Manager.
- **iOS:** Install iOS Device Bridge (`idb`).
  - macOS: `brew tap facebook/fb && brew install idb-companion`
  - For more details, see [Meta's IDB repository](https://github.com/facebook/idb).

*Note: The MCP server and CLI will only work if these tools are successfully installed and discoverable in your PATH.*

## The Problem vs. Our Solution

### The Problem
Sending raw UI XML or massive Vision screenshots directly to an LLM for automation testing is incredibly inefficient. It consumes a huge number of tokens, increases latency, and makes the context window noisy, leading to poor decisions and hallucinations by the LLM.

### The Solution: Token-Diet Architecture
AgenticADB employs a "Token-Diet" architecture. We extract the raw XML/JSON from devices, filter out useless noise (invisible or non-interactable elements), and parse it into a **minified JSON format**.

Furthermore, we pre-calculate the exact center coordinates (`center_x`, `center_y`) for every UI element. This means the LLM no longer has to perform complex math or guess bounding box coordinates. It just receives a clean, flattened JSON array of interactable elements and exact coordinates to tap!

## Key Features
- **FastMCP Integration:** Instantly expose mobile automation tools to Claude Desktop, Cursor, or any MCP-compatible agent.
- **Cross-Platform Adapter Pattern:** A unified API for both Android (`adb`) and iOS (`idb`). The LLM uses the exact same commands regardless of the platform.
- **Math-Free AI:** Bounding boxes are converted to explicit integer coordinates, drastically reducing LLM hallucinations.
- **Auto-Resilience:** Built-in timeouts and automatic retry mechanisms ensure shell execution resilience against daemon hangs.

## Installation

**Strict Requirement:** AgenticADB requires **Python 3.10 or higher**.

Clone the repository and install the dependencies:

```bash
git clone https://github.com/your-org/AgenticADB.git
cd AgenticADB
pip install -r requirements.txt
```

## Usage (MCP Server)

AgenticADB provides an MCP (Model Context Protocol) server to instantly grant your LLM agents the ability to interact with connected devices.

### Adding to Claude Desktop

Edit your `claude_desktop_config.json` file (usually located at `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS) and add the following configuration.

**Make sure to replace `<ABSOLUTE_PATH_TO_AGENTIC_ADB_REPO>` with the actual absolute path to your cloned repository.**

```json
{
  "mcpServers": {
    "agentic_adb": {
      "command": "python3",
      "args": ["<ABSOLUTE_PATH_TO_AGENTIC_ADB_REPO>/AgenticADB/mcp_server.py"]
    }
  }
}
```

### Adding to Cursor IDE

To use AgenticADB directly inside Cursor IDE as an MCP server:

1. Open Cursor Settings.
2. Navigate to **Features > MCP**.
3. Add a new server with the following details:
   - **Type:** `stdio`
   - **Command:** `python3 <ABSOLUTE_PATH_TO_AGENTIC_ADB_REPO>/AgenticADB/mcp_server.py`

## Usage (CLI)

You can also use AgenticADB directly from the command line to fetch the current UI state.

```bash
# Ensure you are in the root directory and your PYTHONPATH is set
PYTHONPATH=AgenticADB python3 AgenticADB/main.py --os android
PYTHONPATH=AgenticADB python3 AgenticADB/main.py --os ios --device <UDID>
```
