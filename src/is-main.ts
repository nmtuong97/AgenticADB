import { realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";

export function isMain(metaUrl: string): boolean {
	if (typeof process === "undefined" || !process.argv || !process.argv[1]) {
		return false;
	}
	try {
		const scriptPath = realpathSync(process.argv[1]);
		const modulePath = realpathSync(fileURLToPath(metaUrl));
		return scriptPath === modulePath;
	} catch (_e) {
		return false;
	}
}
