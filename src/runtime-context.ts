import { AdbClient } from "./client/adb-client.js";
import { IdbClient } from "./client/idb-client.js";
import { smartDeviceRouting } from "./device-utils.js";
import { AdbParser } from "./parser/adb-parser.js";
import { IdbParser } from "./parser/idb-parser.js";
import { UIActionService } from "./service/ui-action-service.js";
import { UIQueryService } from "./service/ui-query-service.js";

export async function getServices(
	osOpt?: string,
	deviceOpt?: string,
): Promise<{
	queryService: UIQueryService;
	actionService: UIActionService;
	client: AdbClient | IdbClient;
	parser: AdbParser | IdbParser;
	os: "android" | "ios";
	deviceId: string | null;
}> {
	const { os, deviceId } = await smartDeviceRouting(deviceOpt, osOpt);

	let client: AdbClient | IdbClient;
	let parser: AdbParser | IdbParser;

	if (os === "android") {
		client = new AdbClient(deviceId);
		parser = new AdbParser();
	} else {
		client = new IdbClient(deviceId);
		parser = new IdbParser();
	}

	return {
		queryService: new UIQueryService(client, parser as any),
		actionService: new UIActionService(client),
		client,
		parser,
		os,
		deviceId,
	};
}
