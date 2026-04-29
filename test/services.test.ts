import { beforeEach, describe, expect, it, vi } from "vitest";
import type { BaseClient } from "../src/client/adb-client.js";
import type { BaseParser } from "../src/parser/adb-parser.js";
import { UIActionService } from "../src/service/ui-action-service.js";
import { UIQueryService } from "../src/service/ui-query-service.js";

describe("Services", () => {
	let mockClient: any;
	let mockParser: any;

	beforeEach(() => {
		mockClient = {
			dumpUI: vi.fn(),
			tap: vi.fn(),
			swipe: vi.fn(),
			inputText: vi.fn(),
			longPress: vi.fn(),
			pressKey: vi.fn(),
			launchApp: vi.fn(),
			killApp: vi.fn(),
		};

		mockParser = {
			parse: vi.fn(),
		};
	});

	describe("UIQueryService", () => {
		it("should query UI", async () => {
			mockClient.dumpUI.mockResolvedValue("<xml></xml>");
			const mockElements = [{ class: "test" }];
			mockParser.parse.mockReturnValue(mockElements);

			const service = new UIQueryService(
				mockClient as BaseClient,
				mockParser as BaseParser,
			);
			const result = await service.getCurrentUI();

			expect(mockClient.dumpUI).toHaveBeenCalledTimes(1);
			expect(mockParser.parse).toHaveBeenCalledWith("<xml></xml>");
			expect(result).toBe(mockElements);
		});

		it("should handle empty dump correctly", async () => {
			mockClient.dumpUI.mockResolvedValue("");
			const service = new UIQueryService(
				mockClient as BaseClient,
				mockParser as BaseParser,
			);
			const result = await service.getCurrentUI();
			expect(result).toEqual([]);
			expect(mockParser.parse).not.toHaveBeenCalled();
		});
	});

	describe("UIActionService", () => {
		it("should proxy tap correctly", async () => {
			const service = new UIActionService(mockClient as BaseClient);
			await service.tapCoordinate(10, 20);
			expect(mockClient.tap).toHaveBeenCalledWith(10, 20);
		});

		it("should proxy swipe correctly", async () => {
			const service = new UIActionService(mockClient as BaseClient);
			await service.swipeScreen(10, 20, 30, 40, 500);
			expect(mockClient.swipe).toHaveBeenCalledWith(10, 20, 30, 40, 500);
		});

		it("should error on invalid coordinates", async () => {
			const service = new UIActionService(mockClient as BaseClient);
			await expect(service.tapCoordinate(-1, 10)).rejects.toThrow();
			await expect(service.tapCoordinate(Number.NaN, 10)).rejects.toThrow();
			await expect(
				service.tapCoordinate(10, Number.POSITIVE_INFINITY),
			).rejects.toThrow();

			await expect(service.swipeScreen(10, -20, 30, 40)).rejects.toThrow();
			await expect(
				service.swipeScreen(10, 20, 30, 40, Number.NaN),
			).rejects.toThrow();

			await expect(
				service.longPressCoordinate(Number.NEGATIVE_INFINITY, 100),
			).rejects.toThrow();
			await expect(service.longPressCoordinate(100, 100, -1)).rejects.toThrow();
		});
	});
});
