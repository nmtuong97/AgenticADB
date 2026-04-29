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
			await client.dumpUI();
			expect(baseClient.runCommand).toHaveBeenCalledWith(
				"adb",
				["-s", "dev123", "exec-out", "uiautomator", "dump", "/dev/tty"],
				expect.any(Object),
			);
		});

		it("should format inputText and escape spaces", async () => {
			const client = new AdbClient();
			await client.inputText("hello world");
			expect(baseClient.runCommand).toHaveBeenCalledWith("adb", [
				"shell",
				"input",
				"text",
				"hello%sworld",
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
