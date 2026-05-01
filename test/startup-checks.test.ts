import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { runCommand } from "../src/client/base-client.js";
import { checkDependencies } from "../src/startup-checks.js";

vi.mock("../src/client/base-client.js", () => ({
	runCommand: vi.fn(),
}));

describe("Startup Checks", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	it("should pass if targetOs is android and adb is present", async () => {
		vi.mocked(runCommand).mockResolvedValueOnce("Android Debug Bridge version");
		await expect(checkDependencies("android")).resolves.not.toThrow();
		expect(runCommand).toHaveBeenCalledWith(
			"adb",
			["version"],
			expect.any(Object),
		);
	});

	it("should throw if targetOs is android and adb is missing", async () => {
		vi.mocked(runCommand).mockRejectedValueOnce(new Error("ENOENT"));
		await expect(checkDependencies("android")).rejects.toThrow(
			"ADB is not installed or not in PATH.",
		);
	});

	it("should pass if targetOs is ios and idb is present", async () => {
		vi.mocked(runCommand).mockResolvedValueOnce("idb version");
		await expect(checkDependencies("ios")).resolves.not.toThrow();
		expect(runCommand).toHaveBeenCalledWith(
			"idb",
			["--version"],
			expect.any(Object),
		);
	});

	it("should throw if targetOs is ios and idb is missing", async () => {
		vi.mocked(runCommand).mockRejectedValueOnce(new Error("ENOENT"));
		await expect(checkDependencies("ios")).rejects.toThrow(
			"IDB is not installed or not in PATH.",
		);
	});

	it("should throw if both adb and idb are missing for MCP server", async () => {
		vi.mocked(runCommand).mockRejectedValue(new Error("ENOENT"));
		await expect(checkDependencies()).rejects.toThrow(
			"Neither ADB nor IDB are installed or in PATH.",
		);
	});

	it("should log warning if only adb is missing for MCP server", async () => {
		const warnSpy = vi.spyOn(console, "error").mockImplementation(() => {});
		vi.mocked(runCommand).mockImplementation(async (cmd) => {
			if (cmd === "adb") throw new Error("ENOENT");
			return "idb version";
		});

		await expect(checkDependencies()).resolves.not.toThrow();
		expect(warnSpy).toHaveBeenCalledWith(
			"Warning: adb not found, Android support disabled.",
		);
		warnSpy.mockRestore();
	});

	it("should log warning if only idb is missing for MCP server", async () => {
		const warnSpy = vi.spyOn(console, "error").mockImplementation(() => {});
		vi.mocked(runCommand).mockImplementation(async (cmd) => {
			if (cmd === "idb") throw new Error("ENOENT");
			return "adb version";
		});

		await expect(checkDependencies()).resolves.not.toThrow();
		expect(warnSpy).toHaveBeenCalledWith(
			"Warning: idb not found, iOS support disabled.",
		);
		warnSpy.mockRestore();
	});
});
