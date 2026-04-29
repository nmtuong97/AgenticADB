import { runCommand } from "./client/base-client.js";

export async function detectAndroidDevices(): Promise<string[]> {
	try {
		const output = await runCommand("adb", ["devices"], { timeout: 5000 });
		const lines = output.split("\n");
		const devices: string[] = [];
		for (const line of lines) {
			if (line.includes("List of devices attached")) continue;
			const match = line.match(/^(\S+)\s+device$/);
			if (match) {
				devices.push(match[1]);
			}
		}
		return devices;
	} catch (_e) {
		return [];
	}
}

export async function detectIosDevices(): Promise<string[]> {
	try {
		const output = await runCommand("idb", ["list-targets"], { timeout: 5000 });
		const lines = output.split("\n");
		const devices: string[] = [];
		for (const line of lines) {
			if (!line.trim()) continue;
			const parts = line.split("|").map((p) => p.trim());
			if (parts.length >= 3 && parts[2].toLowerCase() === "booted") {
				devices.push(parts[0]);
			}
		}
		return devices;
	} catch (_e) {
		return [];
	}
}

export async function smartDeviceRouting(
	deviceOpt?: string,
	osOpt?: string,
): Promise<{ os: "android" | "ios"; deviceId: string | null }> {
	if (osOpt) {
		const lowerOs = osOpt.toLowerCase();
		if (lowerOs === "android" || lowerOs === "ios") {
			return { os: lowerOs, deviceId: deviceOpt || null };
		}
		throw new Error(`Unsupported OS: ${osOpt}`);
	}

	const [androidDevices, iosDevices] = await Promise.all([
		detectAndroidDevices(),
		detectIosDevices(),
	]);

	if (deviceOpt) {
		if (androidDevices.includes(deviceOpt)) {
			return { os: "android", deviceId: deviceOpt };
		}
		if (iosDevices.includes(deviceOpt)) {
			return { os: "ios", deviceId: deviceOpt };
		}
		throw new Error(`Device ${deviceOpt} not found in active devices list.`);
	}

	const total = androidDevices.length + iosDevices.length;
	if (total === 1) {
		if (androidDevices.length === 1) {
			return { os: "android", deviceId: androidDevices[0] };
		} else {
			return { os: "ios", deviceId: iosDevices[0] };
		}
	}

	if (total > 1) {
		throw new Error(
			"Multiple devices connected. Please specify --device or --os.",
		);
	}

	throw new Error("No devices detected.");
}
