import { runCommand } from "./client/base-client.js";

export async function checkDependencies(
	targetOs?: "android" | "ios",
): Promise<void> {
	const checkAdb = async () => {
		try {
			await runCommand("adb", ["version"], { timeout: 5000 });
			return true;
		} catch (e) {
			return false;
		}
	};

	const checkIdb = async () => {
		try {
			await runCommand("idb", ["--version"], { timeout: 5000 });
			return true;
		} catch (e) {
			return false;
		}
	};

	if (targetOs === "android") {
		const hasAdb = await checkAdb();
		if (!hasAdb) {
			throw new Error("ADB is not installed or not in PATH.");
		}
	} else if (targetOs === "ios") {
		const hasIdb = await checkIdb();
		if (!hasIdb) {
			throw new Error("IDB is not installed or not in PATH.");
		}
	} else {
		const [hasAdb, hasIdb] = await Promise.all([checkAdb(), checkIdb()]);
		if (!hasAdb && !hasIdb) {
			throw new Error("Neither ADB nor IDB are installed or in PATH.");
		}
		if (!hasAdb) {
			console.error("Warning: adb not found, Android support disabled.");
		}
		if (!hasIdb) {
			console.error("Warning: idb not found, iOS support disabled.");
		}
	}
}
