# AgenticADB: The Autonomous AI Guide (AGENTS.md)

Welcome, Autonomous AI Agent (like Jules). This file is your absolute Source of Truth for navigating, understanding, and modifying the `AgenticADB` repository. It is designed to maximize your token efficiency and execution success.

## 1. Project Mission & Principles

AgenticADB is a token-efficient Android and iOS UI parser designed specifically for LLM Agents. Our core philosophies dictate all architectural decisions:

### The "Token-Diet" Philosophy
Raw XML (Android) and JSON (iOS) dumps from devices are massively bloated and consume excessive context window tokens. Our primary mission is to minify these dumps into highly compressed, clean JSON. We strip out unnecessary attributes, hidden nodes, and layout containers to feed only the most critical, actionable UI elements to the LLM.

### The "Adapter Pattern" & Universal UI Contract
We unify Android (`adb`) and iOS (`idb`) interactions under a single interface. The ultimate goal of this pattern is to force both the `adb_client` and `idb_parser` to output the exact same Dataclasses defined in `models.py`. This acts as our "Universal UI Contract" for the LLM, ensuring that downstream decision-making logic remains platform-agnostic. Interface method signatures must be strictly identical across both platforms (ignoring unneeded arguments internally if necessary).

### "Math-Free AI"
LLMs are notorious for hallucinating when doing math or dealing with arrays. To prevent this, we never require the LLM to calculate coordinates. We pre-calculate center coordinates in Python before outputting the JSON.
**Rule:** Represent UI coordinates using explicit integer keys (`center_x`, `center_y`) calculated via integer division. Never use floats or arrays, as explicit keys drastically reduce LLM hallucination when generating follow-up tap commands.

---

## 2. Technical Stack & Workspace Setup

- **Language:** Python 3.10+
- **Libraries:** Primarily standard Python libraries to reduce dependencies. The official `mcp` package is permitted for the MCP server integration.
- **Testing:** `pytest` is used for all unit and integration testing.

### Jules Environment Rules
As an autonomous agent operating in a Cloud VM, you must adhere to the following constraints:
1. **NO PHYSICAL DEVICES OR EMULATORS AVAILABLE.** Do not attempt to start an emulator or connect to a physical device.
2. **Mock Everything:** All `subprocess.run` calls executing raw `adb` or `idb` commands **MUST** be 100% mocked in tests using `unittest.mock`. This prevents the test suite from hanging in cloud environments.
3. **Strict Output Control:** All debug logging must be routed to `stderr`. Standard output (`stdout`) must remain perfectly clean for JSON-RPC / MCP communication. Extraneous prints will break the server.
4. **Communication Rule:** Communicate with the user in Vietnamese (Tiếng Việt), but keep all code, variable names, and technical terms in English.

---

## 3. The Agentic Skills (Goal-Driven Execution)

Follow these Karpathy-inspired skills. Transform your imperative instructions into declarative goals with verification loops.

### Skill: `run_tdd_loop`
- **Description:** Implement features or fix bugs using Test-Driven Development. Loop autonomously until successful.
- **Tools used:** `pytest`, `unittest.mock`
- **Step-by-step instructions:**
  1. **Goal:** Write a failing test that reproduces the expected behavior or bug first.
  2. Run `pytest` to confirm it fails.
  3. Write the implementation code.
  4. Run `pytest` again. Read the traceback in `stderr`/`stdout`, identify the flawed logic (in test or source), apply the fix, and loop.
  5. **Do not stop until 100% tests pass.** Never ask for human permission during the loop.

### Skill: `inspect_ui`
- **Description:** Parse a raw UI dump from a mock source into minified JSON.
- **Tools used:** `adb_client.py` or `idb_client.py`, `models.py`
- **Step-by-step instructions:**
  1. **Goal:** Verify that a raw platform-specific mock dump (e.g., `mock_android_dump.xml`) parses successfully into the universal `models.py` dataclasses.
  2. Feed the mock data into the appropriate parser.
  3. Verify the output JSON contains only the required `snake_case` keys (like `center_x`, `center_y`, `text`, `class_name`).
  4. If noise nodes or missing coordinates are detected, adjust the filtering logic in `parser.py` and run the TDD loop.

### Skill: `perform_action`
- **Description:** Execute a UI action (tap, swipe, input text) safely via the device clients.
- **Tools used:** `adb_client.py`, `idb_client.py`
- **Step-by-step instructions:**
  1. **Goal:** Send the correct shell-escaped command to the device without exposing complexity to the LLM.
  2. The device clients must completely abstract shell-escaping complexity away from the LLM.
  3. Write a test asserting that the correct `subprocess.run` arguments were called for a given high-level action.
  4. Implement the escaping and subprocess call logic. Loop via TDD until the test passes.

---

## 4. Code Style & Architecture Guidelines

### Folder Structure Overview
```text
AgenticADB/
├── agentic_adb/
│   ├── adb_client.py    # Android implementation
│   ├── idb_client.py    # iOS implementation
│   ├── models.py        # Universal UI Contract (Dataclasses)
│   └── parser.py        # Core logic for stripping prefixes/noise
├── tests/
│   ├── mock_data/       # Strictly separated mock files (e.g., mock_android_dump.xml, mock_ios_dump.json)
│   └── ...
├── main.py              # CLI entrypoint
└── mcp_server.py        # FastMCP Server integration
```

### Models & Naming Conventions (`models.py`)
- **Classes:** Use standard `CamelCase` for all Python Dataclasses (e.g., `UIElement`, `DeviceState`). Always use Python `dataclasses` to ensure strong typing.
- **JSON Output:** Strictly mandate `snake_case` for all exported JSON keys (e.g., `center_x`, `is_clickable`). This ensures stable and predictable LLM parsing.

### Parser Rules (`parser.py`)
- The parser must rigorously strip out XML/JSON prefixes and filter out "noise" nodes (e.g., invisible layout containers, empty elements without descriptions).
- UI elements parsed from either Android or iOS must be mapped to the exact same shared dataclass objects.

---

## 5. Testing & Validation Protocol

### Running Tests
Run the test suite using:
```bash
PYTHONPATH=AgenticADB python3 -m pytest -v AgenticADB/tests
```

### The "Self-Healing Loop"
When testing, embody the Goal-Driven Execution principle. If a test fails:
1. Execute `pytest`.
2. Read the full traceback in `stderr`/`stdout`.
3. Identify the flawed logic (whether it resides in the test file or the source code).
4. Apply the targeted fix.
5. Loop back to Step 1.
**Do not stop until 100% of the tests pass.**

### Mock Data Strictness
Maintain strictly separated mock data files for each platform's parsing tests. Do not combine them. Use `mock_android_dump.xml` for ADB and `mock_ios_dump.json` for IDB.

### CLI Testing Anti-Pattern
For CLI testing (`main.py`), avoid the anti-pattern of mocking `sys.argv` and catching `sys.exit`. Instead, extract the inner CLI logic into a testable function (e.g., `run_cli(args: list[str])`) to keep core logic isolated from the global `sys` state.

---

## 6. MCP Server Integration

The AgenticADB MCP server is located at `mcp_server.py` and uses `FastMCP` over standard `stdio` transport.

### Running the Server
Start the server simply by running the python file:
```bash
python mcp_server.py
```

### Error Handling
All tool errors (e.g., subprocess failures) **must** be caught and returned as clear string messages (e.g., `"Action failed: ..."`) rather than raising Python exceptions. This prevents the MCP server from crashing unexpectedly.

### Claude Desktop Configuration
To integrate this server into Claude Desktop, add the following snippet to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "agentic_adb": {
      "command": "python",
      "args": ["<absolute_path_to_repo>/AgenticADB/mcp_server.py"]
    }
  }
}
```
*(Replace `<absolute_path_to_repo>` with the actual absolute path to the repository on your machine).*
