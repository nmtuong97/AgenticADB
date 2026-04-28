import { runCommand } from "./base-client.js";

export interface BaseClient {
	deviceId: string | null;
	dumpUI(): Promise<string>;
	tap(x: number, y: number): Promise<void>;
	swipe(
		startX: number,
		startY: number,
		endX: number,
		endY: number,
		durationMs?: number,
	): Promise<void>;
	inputText(text: string): Promise<void>;
	longPress(x: number, y: number, durationMs?: number): Promise<void>;
	pressKey(key: string): Promise<void>;
	launchApp(appId: string): Promise<void>;
	killApp(appId: string): Promise<void>;
}

export class AdbClient implements BaseClient {
	constructor(public deviceId: string | null = null) {}

	private getBaseArgs(): string[] {
		return this.deviceId ? ["-s", this.deviceId] : [];
	}

	async dumpUI(): Promise<string> {
		const args = [
			...this.getBaseArgs(),
			"exec-out",
			"uiautomator",
			"dump",
			"/dev/tty",
		];
		return await runCommand("adb", args, { retry: true, timeout: 15000 });
	}

	async tap(x: number, y: number): Promise<void> {
		const args = [
			...this.getBaseArgs(),
			"shell",
			"input",
			"tap",
			x.toString(),
			y.toString(),
		];
		await runCommand("adb", args);
	}

	async swipe(
		startX: number,
		startY: number,
		endX: number,
		endY: number,
		durationMs = 300,
	): Promise<void> {
		const args = [
			...this.getBaseArgs(),
			"shell",
			"input",
			"swipe",
			startX.toString(),
			startY.toString(),
			endX.toString(),
			endY.toString(),
			durationMs.toString(),
		];
		await runCommand("adb", args);
	}

	async inputText(text: string): Promise<void> {
		const escapedText = text.replace(/ /g, "%s");
		const args = [...this.getBaseArgs(), "shell", "input", "text", escapedText];
		await runCommand("adb", args);
	}

	async longPress(x: number, y: number, durationMs = 1000): Promise<void> {
		const args = [
			...this.getBaseArgs(),
			"shell",
			"input",
			"swipe",
			x.toString(),
			y.toString(),
			x.toString(),
			y.toString(),
			durationMs.toString(),
		];
		await runCommand("adb", args);
	}

	async pressKey(key: string): Promise<void> {
		let keycode = key;
		const keyMap: Record<string, string> = {
			home: "KEYCODE_HOME",
			back: "KEYCODE_BACK",
			enter: "KEYCODE_ENTER",
			volume_up: "KEYCODE_VOLUME_UP",
			volume_down: "KEYCODE_VOLUME_DOWN",
		};
		if (keyMap[key.toLowerCase()]) {
			keycode = keyMap[key.toLowerCase()];
		}
		const args = [...this.getBaseArgs(), "shell", "input", "keyevent", keycode];
		await runCommand("adb", args);
	}

	async launchApp(appId: string): Promise<void> {
		const args = [
			...this.getBaseArgs(),
			"shell",
			"monkey",
			"-p",
			appId,
			"-c",
			"android.intent.category.LAUNCHER",
			"1",
		];
		await runCommand("adb", args);
	}

	async killApp(appId: string): Promise<void> {
		const args = [...this.getBaseArgs(), "shell", "am", "force-stop", appId];
		await runCommand("adb", args);
	}
}
