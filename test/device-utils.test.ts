import { beforeEach, describe, expect, it, vi } from "vitest";
import * as baseClient from "../src/client/base-client.js";
import {
	detectAndroidDevices,
	detectIosDevices,
	smartDeviceRouting,
} from "../src/device-utils.js";

vi.mock("../src/client/base-client.js", () => ({
	runCommand: vi.fn(),
	CommandError: class CommandError extends Error {},
	ParseError: class ParseError extends Error {},
	DeviceNotFoundError: class DeviceNotFoundError extends Error {},
	AgenticADBError: class AgenticADBError extends Error {},
}));

describe("Smart Device Routing", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("detectAndroidDevices should parse adb devices output", async () => {
		vi.mocked(baseClient.runCommand).mockResolvedValueOnce(
			"List of devices attached\nemulator-5554\tdevice\n12345abc\tdevice\noffline-dev\toffline\n",
		);
		const devices = await detectAndroidDevices();
		expect(devices).toEqual(["emulator-5554", "12345abc"]);
	});

	it("detectIosDevices should parse idb list-targets output", async () => {
		vi.mocked(baseClient.runCommand).mockResolvedValueOnce(
			"00008101-00123456789ABCDE | iPhone 13 | Booted | simulator | iOS 15.0\n" +
				"1234-5678 | iPhone 12 | Shutdown | simulator | iOS 14.4\n",
		);
		const devices = await detectIosDevices();
		expect(devices).toEqual(["00008101-00123456789ABCDE"]);
	});

	it("should route to android if os is specified as android", async () => {
		const result = await smartDeviceRouting("my-device", "android");
		expect(result).toEqual({ os: "android", deviceId: "my-device" });
	});

	it("should route to ios if os is specified as ios", async () => {
		const result = await smartDeviceRouting("my-device", "ios");
		expect(result).toEqual({ os: "ios", deviceId: "my-device" });
	});

	it("should auto-detect os if device ID matches android list", async () => {
		vi.mocked(baseClient.runCommand).mockImplementation(async (cmd) => {
			if (cmd === "adb")
				return "List of devices attached\nemulator-5554\tdevice\n";
			if (cmd === "idb") return "";
			return "";
		});

		const result = await smartDeviceRouting("emulator-5554");
		expect(result).toEqual({ os: "android", deviceId: "emulator-5554" });
	});

	it("should fail if device is specified but not found", async () => {
		vi.mocked(baseClient.runCommand).mockResolvedValue("");
		await expect(smartDeviceRouting("unknown")).rejects.toThrow(
			/not found in active devices list/,
		);
	});

	it("should auto-use the only connected device if no args passed", async () => {
		vi.mocked(baseClient.runCommand).mockImplementation(async (cmd) => {
			if (cmd === "adb") return "List of devices attached\n";
			if (cmd === "idb")
				return "00008101-00123456789ABCDE | iPhone 13 | Booted | simulator | iOS 15.0\n";
			return "";
		});
		const result = await smartDeviceRouting();
		expect(result).toEqual({
			os: "ios",
			deviceId: "00008101-00123456789ABCDE",
		});
	});

	it("should fail if multiple devices connected and no args passed", async () => {
		vi.mocked(baseClient.runCommand).mockImplementation(async (cmd) => {
			if (cmd === "adb")
				return "List of devices attached\nemulator-5554\tdevice\n";
			if (cmd === "idb")
				return "00008101-00123456789ABCDE | iPhone 13 | Booted | simulator | iOS 15.0\n";
			return "";
		});
		await expect(smartDeviceRouting()).rejects.toThrow(
			/Multiple devices connected/,
		);
	});
});
