# JULES AGENT PROMPT: AgenticADB Production-Ready Refactoring

Hello Jules. You are operating in the `AgenticADB` repository. 
Before starting, **you MUST read `AGENTS.md`** to understand the project's philosophy, "Token-Diet" approach, and strict constraints (e.g., mocking everything in tests, stderr logging only).

**Goal:** Refactor the codebase to make it robust, secure, and production-ready by resolving 5 specific issues. Use your `run_tdd_loop` skill for each task. Write failing tests first, implement the fix, and ensure 100% test pass rate.

---

### Task 1: Robustness & Error Recovery (Uiautomator & Timeout)
1. **ADB Uiautomator Hang Recovery (`src/client/adb-client.ts`):** 
   - `uiautomator dump` frequently hangs or returns an idle state error on real devices.
   - **Action:** Update the `dumpUI()` method. If the `runCommand` for dumping fails or times out, catch the error, execute `adb shell pkill -f uiautomator` (or equivalent) to reset the service on the device, and then retry the `dump` command exactly once before giving up.
2. **Reliable Timeout Handling (`src/client/base-client.ts`):**
   - The current timeout check relies on fragile string matching (`error.message.includes("signal SIGTERM")`).
   - **Action:** Refactor the `spawn` error/close handling. Capture the `signal` directly from the `child.on("close", (code, signal) => ...)` event to reliably determine if the process was killed due to a timeout.

### Task 2: Startup Dependency Checks
- **Issue:** If `adb` or `idb` is not installed on the host machine, `spawn` throws an ugly `ENOENT` error.
- **Action:** Implement a startup health check (e.g., running `adb version` and `idb --version` with a short timeout, or checking path). If the required CLI tool for the selected OS is missing, log a human-readable, friendly error message to `stderr` and exit gracefully. Integrate this check into the CLI (`src/cli.ts`) and MCP server (`src/mcp-server.ts`) startup flow.

### Task 3: Security & Command Injection Prevention
- **Issue:** In `src/client/adb-client.ts`, the `inputText` method uses `text.replace(/ /g, "%s")`. This is passed to `adb shell input text`, making it highly vulnerable to command injection if the LLM provides strings containing `&`, `;`, `"`, `'`, or `\`.
- **Action:** Implement a robust shell-escaping utility for Android shell arguments. Properly quote the text input (e.g., wrapping in single quotes and safely escaping inner single quotes) so that complex strings (including special characters) are safely typed on the device without executing rogue shell commands.

### Task 4: Input Validation with Zod (MCP Server)
- **Issue:** In `src/mcp-server.ts`, tool arguments are dangerously cast (e.g., `args.x as number`, `args.text as string`). Hallucinations from LLM clients could crash the server.
- **Action:** 
  1. Install `zod` as a production dependency (`npm i zod`).
  2. Define strict Zod schemas for every tool's input arguments.
  3. Parse `request.params.arguments` using these schemas. If parsing fails, catch the Zod error and return a clear formatting error message in the MCP `content` array (with `isError: true`), preventing a server crash.

### Task 5: Parser Edge Cases (iOS IDB JSON Noise)
- **Issue:** `idb ui describe-all` occasionally outputs plain-text warnings before or after the actual JSON payload. The current `IdbParser.parse` assumes the input is a perfect JSON string, which causes `JSON.parse` to throw a `SyntaxError`.
- **Action:** Update `src/parser/idb-parser.ts`. Before calling `JSON.parse`, use logic (like regex or string indexing) to extract the first occurrence of `{` or `[` up to the last occurrence of `}` or `]`. Ensure it can gracefully ignore non-JSON prefix/suffix noise.

---
**Execution Rules:**
- Do not ask for permission between steps.
- Write unit tests for your changes (especially the shell escaping, Zod validation, and JSON extracting). 
- Ensure `npm run check` (tests, lint, typecheck) passes completely.
