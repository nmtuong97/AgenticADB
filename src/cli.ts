#!/usr/bin/env node
import { Command } from "commander";
import { AdbClient } from "./client/adb-client.js";
import { IdbClient } from "./client/idb-client.js";
import { smartDeviceRouting } from "./device-utils.js";
import { runMcpServer } from "./mcp-server.js";
import { AdbParser } from "./parser/adb-parser.js";
import { IdbParser } from "./parser/idb-parser.js";
import { UIActionService } from "./service/ui-action-service.js";
import { UIQueryService } from "./service/ui-query-service.js";

export async function runCli(args: string[]) {
	const program = new Command();

	program
		.name("aadb")
		.description("AgenticADB: Autonomous UI parser and interaction tool")
		.version("1.0.0")
		.option("-d, --device <id>", "Target device ID")
		.option("--os <os>", "Target OS (android or ios)");

	async function getServices(options: Record<string, string>) {
		const { os, deviceId } = await smartDeviceRouting(
			options.device,
			options.os,
		);
		let client: any, parser: any;

		if (os === "android") {
			client = new AdbClient(deviceId);
			parser = new AdbParser();
		} else {
			client = new IdbClient(deviceId);
			parser = new IdbParser();
		}

		const queryService = new UIQueryService(client, parser);
		const actionService = new UIActionService(client);
		return { queryService, actionService };
	}

	program
		.command("dump")
		.description("Dump the current UI hierarchy as minified JSON")
		.option(
			"--raw",
			"Return the raw XML/JSON output instead of parsed elements",
		)
		.option("-o, --output <filepath>", "Save the output to a specific file")
		.action(async (options) => {
			try {
				const { queryService } = await getServices(program.opts());
				let outData: string;
				if (options.raw) {
					const { os, deviceId } = await smartDeviceRouting(
						program.opts().device,
						program.opts().os,
					);
					const client =
						os === "android"
							? new AdbClient(deviceId)
							: new IdbClient(deviceId);
					outData = await client.dumpUI();
				} else {
					const ui = await queryService.getCurrentUI();
					outData = JSON.stringify(ui, null, 2);
				}

				if (options.output) {
					const fs = await import("node:fs");
					fs.writeFileSync(options.output, outData);
					console.log(`Dump saved to ${options.output}`);
				} else {
					console.log(outData);
				}
			} catch (e: any) {
				console.error(`Error: ${e.message}`);
				process.exit(1);
			}
		});

	program
		.command("tap <x> <y>")
		.description("Tap at specific coordinates")
		.action(async (x, y) => {
			try {
				const { actionService } = await getServices(program.opts());
				await actionService.tapCoordinate(parseInt(x, 10), parseInt(y, 10));
			} catch (e: any) {
				console.error(`Error: ${e.message}`);
				process.exit(1);
			}
		});

	program
		.command("swipe <x1> <y1> <x2> <y2> [duration]")
		.description("Swipe from x1,y1 to x2,y2")
		.action(async (x1, y1, x2, y2, duration) => {
			try {
				const { actionService } = await getServices(program.opts());
				await actionService.swipeScreen(
					parseInt(x1, 10),
					parseInt(y1, 10),
					parseInt(x2, 10),
					parseInt(y2, 10),
					duration ? parseInt(duration, 10) : 300,
				);
			} catch (e: any) {
				console.error(`Error: ${e.message}`);
				process.exit(1);
			}
		});

	program
		.command("input <text>")
		.description("Input text")
		.action(async (text) => {
			try {
				const { actionService } = await getServices(program.opts());
				await actionService.inputTextField(text);
			} catch (e: any) {
				console.error(`Error: ${e.message}`);
				process.exit(1);
			}
		});

	program
		.command("long_press <x> <y> [duration]")
		.description("Long press at specific coordinates")
		.action(async (x, y, duration) => {
			try {
				const { actionService } = await getServices(program.opts());
				await actionService.longPressCoordinate(
					parseInt(x, 10),
					parseInt(y, 10),
					duration ? parseInt(duration, 10) : 1000,
				);
			} catch (e: any) {
				console.error(`Error: ${e.message}`);
				process.exit(1);
			}
		});

	program
		.command("press <key>")
		.description("Press a system key (home, back, enter, etc.)")
		.action(async (key) => {
			try {
				const { actionService } = await getServices(program.opts());
				await actionService.pressSystemKey(key);
			} catch (e: any) {
				console.error(`Error: ${e.message}`);
				process.exit(1);
			}
		});

	program
		.command("launch <appId>")
		.description("Launch an application")
		.action(async (appId) => {
			try {
				const { actionService } = await getServices(program.opts());
				await actionService.launchApplication(appId);
			} catch (e: any) {
				console.error(`Error: ${e.message}`);
				process.exit(1);
			}
		});

	program
		.command("kill <appId>")
		.description("Kill an application")
		.action(async (appId) => {
			try {
				const { actionService } = await getServices(program.opts());
				await actionService.killApplication(appId);
			} catch (e: any) {
				console.error(`Error: ${e.message}`);
				process.exit(1);
			}
		});

	program
		.command("mcp-server")
		.description("Start the AgenticADB MCP server via stdio")
		.action(async () => {
			try {
				await runMcpServer(process.argv);
			} catch (e: any) {
				console.error(`Error: ${e.message}`);
				process.exit(1);
			}
		});

	if (typeof process !== "undefined" && process.env.NODE_ENV !== "test") {
		program.parse(args);
	} else {
		return program.parseAsync(args);
	}
}

import { fileURLToPath } from "node:url";

const isMain =
	typeof process !== "undefined" &&
	process.argv[1] === fileURLToPath(import.meta.url);
if (isMain) {
	runCli(process.argv);
}
