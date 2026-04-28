import { beforeEach, describe, expect, it, vi } from "vitest";
import { runCli } from "../src/cli.js";
import * as deviceUtils from "../src/device-utils.js";
import { UIActionService } from "../src/service/ui-action-service.js";
import { UIQueryService } from "../src/service/ui-query-service.js";

vi.mock("../src/device-utils.js");
vi.mock("../src/service/ui-query-service.js");
vi.mock("../src/service/ui-action-service.js");

describe("CLI Dispatch", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		vi.spyOn(console, "log").mockImplementation(() => {});
		vi.spyOn(console, "error").mockImplementation(() => {});

		vi.mocked(deviceUtils.smartDeviceRouting).mockResolvedValue({
			os: "android",
			deviceId: "123",
		});
	});

	it("should call dump and output JSON", async () => {
		const mockGetCurrentUI = vi.fn().mockResolvedValue([{ class: "Button" }]);
		UIQueryService.prototype.getCurrentUI = mockGetCurrentUI;

		await runCli(["node", "aadb", "dump"]);

		expect(deviceUtils.smartDeviceRouting).toHaveBeenCalled();
		expect(mockGetCurrentUI).toHaveBeenCalled();
		expect(console.log).toHaveBeenCalledWith(expect.stringContaining("Button"));
	});

	it("should call tap with correct coordinates", async () => {
		const mockTapCoordinate = vi.fn().mockResolvedValue(undefined);
		UIActionService.prototype.tapCoordinate = mockTapCoordinate;

		await runCli(["node", "aadb", "tap", "100", "200"]);

		expect(mockTapCoordinate).toHaveBeenCalledWith(100, 200);
	});

	it("should call swipe with correct coordinates", async () => {
		const mockSwipeScreen = vi.fn().mockResolvedValue(undefined);
		UIActionService.prototype.swipeScreen = mockSwipeScreen;

		await runCli(["node", "aadb", "swipe", "100", "200", "300", "400", "500"]);

		expect(mockSwipeScreen).toHaveBeenCalledWith(100, 200, 300, 400, 500);
	});
});
