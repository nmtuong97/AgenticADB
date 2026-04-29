import type { BaseClient } from "./adb-client.js";
import { runCommand } from "./base-client.js";

export class IdbClient implements BaseClient {
	constructor(public deviceId: string | null = null) {}

	private getBaseArgs(): string[] {
		return this.deviceId ? ["--udid", this.deviceId] : [];
	}

	async dumpUI(): Promise<string> {
		const args = ["ui", "describe-all", ...this.getBaseArgs()];
		return await runCommand("idb", args, { retry: true, timeout: 15000 });
	}

	async tap(x: number, y: number): Promise<void> {
		const args = [
			"ui",
			"tap",
			x.toString(),
			y.toString(),
			...this.getBaseArgs(),
		];
		await runCommand("idb", args);
	}

	async swipe(
		startX: number,
		startY: number,
		endX: number,
		endY: number,
		_durationMs?: number,
	): Promise<void> {
		const args = [
			"ui",
			"swipe",
			startX.toString(),
			startY.toString(),
			endX.toString(),
			endY.toString(),
			...this.getBaseArgs(),
		];
		await runCommand("idb", args);
	}

	async inputText(text: string): Promise<void> {
		const args = ["ui", "text", text, ...this.getBaseArgs()];
		await runCommand("idb", args);
	}

	async longPress(x: number, y: number, _durationMs = 1000): Promise<void> {
		const args = [
			"ui",
			"swipe",
			x.toString(),
			y.toString(),
			x.toString(),
			y.toString(),
			...this.getBaseArgs(),
		];
		await runCommand("idb", args);
	}

	async pressKey(key: string): Promise<void> {
		const keyMap: Record<string, string> = {
			home: "home",
			volume_up: "volume_up",
			volume_down: "volume_down",
		};

		const lowerKey = key.toLowerCase();
		if (lowerKey === "back") {
			console.warn("iOS does not support a hardware back button.");
			return;
		}

		const btn = keyMap[lowerKey] || lowerKey;
		const args = ["ui", "button", btn, ...this.getBaseArgs()];
		await runCommand("idb", args);
	}

	async launchApp(appId: string): Promise<void> {
		const args = ["launch", ...this.getBaseArgs(), appId];
		await runCommand("idb", args);
	}

	async killApp(appId: string): Promise<void> {
		const args = ["terminate", ...this.getBaseArgs(), appId];
		await runCommand("idb", args);
	}
}
