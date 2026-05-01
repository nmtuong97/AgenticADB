import { beforeEach, describe, expect, it, vi } from "vitest";
import { AdbClient } from "../src/client/adb-client.js";
import * as baseClient from "../src/client/base-client.js";
import { IdbClient } from "../src/client/idb-client.js";

vi.mock("../src/client/base-client.js", () => ({
	runCommand: vi.fn(),
}));

describe("Clients", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe("AdbClient", () => {
		it("should format dumpUI correctly", async () => {
			const client = new AdbClient("dev123");
			vi.mocked(baseClient.runCommand).mockResolvedValueOnce("success");
			await client.dumpUI();
			expect(baseClient.runCommand).toHaveBeenCalledWith(
				"adb",
				["-s", "dev123", "exec-out", "uiautomator", "dump", "/dev/tty"],
				{ retry: false, timeout: 15000 },
			);
		});

		it("should recover dumpUI upon failure", async () => {
			const client = new AdbClient("dev123");
			vi.mocked(baseClient.runCommand)
				.mockRejectedValueOnce(new Error("dump failed")) // first dump
				.mockResolvedValueOnce("") // pkill
				.mockResolvedValueOnce("recovered dump"); // second dump

			const result = await client.dumpUI();
			expect(result).toBe("recovered dump");
			expect(baseClient.runCommand).toHaveBeenCalledTimes(3);
			expect(baseClient.runCommand).toHaveBeenNthCalledWith(
				2,
				"adb",
				["-s", "dev123", "shell", "pkill", "-f", "uiautomator"],
				{ retry: false, timeout: 5000 },
			);
			expect(baseClient.runCommand).toHaveBeenNthCalledWith(
				3,
				"adb",
				["-s", "dev123", "exec-out", "uiautomator", "dump", "/dev/tty"],
				{ retry: false, timeout: 15000 },
			);
		});

		it("should format inputText and escape spaces", async () => {
			const client = new AdbClient();
			await client.inputText("hello world");
			expect(baseClient.runCommand).toHaveBeenCalledWith("adb", [
				"shell",
				"input",
				"text",
				"'hello%sworld'",
			]);
		});

		it("should safely shell-escape complex input strings", async () => {
			const client = new AdbClient();
			// Tests command injection attempt: test string containing spaces, single quotes, double quotes, and shell metacharacters
			await client.inputText(`test'ing "; echo "pwned`);
			// "test'ing "; echo "pwned"
			// 1. Space replacement: test'ing%s";%secho%s"pwned
			// 2. Bourne shell escaping (wrap in '', replace ' with '\''):
			// 'test'\''ing%s";%secho%s"pwned'
			expect(baseClient.runCommand).toHaveBeenCalledWith("adb", [
				"shell",
				"input",
				"text",
				`'test'\\''ing%s";%secho%s"pwned'`,
			]);
		});

		it("should translate common keys", async () => {
			const client = new AdbClient();
			await client.pressKey("home");
			expect(baseClient.runCommand).toHaveBeenCalledWith("adb", [
				"shell",
				"input",
				"keyevent",
				"KEYCODE_HOME",
			]);
		});
	});

	describe("IdbClient", () => {
		it("should format tap correctly", async () => {
			const client = new IdbClient("ios123");
			await client.tap(10, 20);
			expect(baseClient.runCommand).toHaveBeenCalledWith("idb", [
				"ui",
				"tap",
				"10",
				"20",
				"--udid",
				"ios123",
			]);
		});

		it("should log warning for back key instead of commanding idb", async () => {
			const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});
			const client = new IdbClient();
			await client.pressKey("back");
			expect(warnSpy).toHaveBeenCalledWith(
				expect.stringContaining("does not support a hardware back button"),
			);
			expect(baseClient.runCommand).not.toHaveBeenCalled();
			warnSpy.mockRestore();
		});

		it("should format swipe correctly", async () => {
			const client = new IdbClient();
			await client.swipe(10, 20, 30, 40);
			expect(baseClient.runCommand).toHaveBeenCalledWith("idb", [
				"ui",
				"swipe",
				"10",
				"20",
				"30",
				"40",
			]);
		});
	});
});
