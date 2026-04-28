import type { BaseClient } from "../client/adb-client.js";

export class UIActionService {
	constructor(private client: BaseClient) {}

	async tapCoordinate(x: number, y: number): Promise<void> {
		if (x == null || y == null || x < 0 || y < 0) {
			throw new Error("Invalid coordinates for tap");
		}
		await this.client.tap(x, y);
	}

	async swipeScreen(
		startX: number,
		startY: number,
		endX: number,
		endY: number,
		durationMs: number = 300,
	): Promise<void> {
		if (startX < 0 || startY < 0 || endX < 0 || endY < 0) {
			throw new Error("Invalid coordinates for swipe");
		}
		await this.client.swipe(startX, startY, endX, endY, durationMs);
	}

	async inputTextField(text: string): Promise<void> {
		if (!text) {
			throw new Error("Input text cannot be empty");
		}
		await this.client.inputText(text);
	}

	async longPressCoordinate(
		x: number,
		y: number,
		durationMs: number = 1000,
	): Promise<void> {
		if (x < 0 || y < 0) {
			throw new Error("Invalid coordinates for long press");
		}
		await this.client.longPress(x, y, durationMs);
	}

	async pressSystemKey(key: string): Promise<void> {
		if (!key) {
			throw new Error("Key cannot be empty");
		}
		await this.client.pressKey(key);
	}

	async launchApplication(appId: string): Promise<void> {
		if (!appId) {
			throw new Error("App ID cannot be empty");
		}
		await this.client.launchApp(appId);
	}

	async killApplication(appId: string): Promise<void> {
		if (!appId) {
			throw new Error("App ID cannot be empty");
		}
		await this.client.killApp(appId);
	}
}
