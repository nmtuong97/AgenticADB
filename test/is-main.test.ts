import * as fs from "node:fs";
import { afterEach, describe, expect, it, vi } from "vitest";
import { isMain } from "../src/is-main.js";

vi.mock("node:fs", () => {
	return {
		realpathSync: vi.fn(),
	};
});

describe("isMain", () => {
	afterEach(() => {
		vi.clearAllMocks();
	});

	it("should return true when scriptPath matches modulePath directly", () => {
		vi.mocked(fs.realpathSync).mockImplementation((path) => String(path));

		const originalArgv = process.argv;
		process.argv = ["node", "/app/src/cli.ts"];

		// Mock import.meta.url
		const result = isMain("file:///app/src/cli.ts");

		expect(result).toBe(true);
		process.argv = originalArgv;
	});

	it("should return true when symlinked bin resolves to modulePath", () => {
		vi.mocked(fs.realpathSync).mockImplementation((path) => {
			if (path === "/usr/local/bin/agentic-adb") return "/app/dist/cli.js";
			if (path === "/app/dist/cli.js") return "/app/dist/cli.js";
			return String(path);
		});

		const originalArgv = process.argv;
		process.argv = ["node", "/usr/local/bin/agentic-adb"];

		// Mock import.meta.url for the compiled file
		const result = isMain("file:///app/dist/cli.js");

		expect(result).toBe(true);
		process.argv = originalArgv;
	});

	it("should return false when scriptPath does not match modulePath", () => {
		vi.mocked(fs.realpathSync).mockImplementation((path) => String(path));

		const originalArgv = process.argv;
		process.argv = ["node", "/app/src/other.ts"];

		const result = isMain("file:///app/src/cli.ts");

		expect(result).toBe(false);
		process.argv = originalArgv;
	});

	it("should return false on fs error (e.g. file not found)", () => {
		vi.mocked(fs.realpathSync).mockImplementation(() => {
			throw new Error("ENOENT");
		});

		const originalArgv = process.argv;
		process.argv = ["node", "/app/src/cli.ts"];

		const result = isMain("file:///app/src/cli.ts");

		expect(result).toBe(false);
		process.argv = originalArgv;
	});
});
