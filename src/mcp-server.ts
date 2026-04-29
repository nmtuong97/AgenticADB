import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
	CallToolRequestSchema,
	ErrorCode,
	ListToolsRequestSchema,
	McpError,
} from "@modelcontextprotocol/sdk/types.js";
import { getServices } from "./runtime-context.js";

export async function runMcpServer(_args: string[]) {
	const server = new Server(
		{
			name: "agentic-adb",
			version: "1.0.0",
		},
		{
			capabilities: {
				tools: {},
			},
		},
	);

	server.setRequestHandler(ListToolsRequestSchema, async () => {
		return {
			tools: [
				{
					name: "get_current_ui",
					description:
						"Dump the current UI hierarchy as a minified JSON structure.",
					inputSchema: {
						type: "object",
						properties: {
							os: {
								type: "string",
								description: "Optional OS ('android' or 'ios')",
							},
							device: { type: "string", description: "Optional Device ID" },
						},
					},
				},
				{
					name: "tap_coordinate",
					description: "Tap at specific coordinates on the device screen.",
					inputSchema: {
						type: "object",
						properties: {
							x: { type: "number", description: "X coordinate" },
							y: { type: "number", description: "Y coordinate" },
							os: { type: "string", description: "Optional OS" },
							device: { type: "string", description: "Optional Device ID" },
						},
						required: ["x", "y"],
					},
				},
				{
					name: "swipe_screen",
					description: "Swipe from one coordinate to another.",
					inputSchema: {
						type: "object",
						properties: {
							x1: { type: "number" },
							y1: { type: "number" },
							x2: { type: "number" },
							y2: { type: "number" },
							duration_ms: { type: "number" },
							os: { type: "string" },
							device: { type: "string" },
						},
						required: ["x1", "y1", "x2", "y2"],
					},
				},
				{
					name: "input_text_field",
					description: "Input text into the currently focused field.",
					inputSchema: {
						type: "object",
						properties: {
							text: { type: "string" },
							os: { type: "string" },
							device: { type: "string" },
						},
						required: ["text"],
					},
				},
				{
					name: "long_press_coordinate",
					description: "Long press at specific coordinates.",
					inputSchema: {
						type: "object",
						properties: {
							x: { type: "number" },
							y: { type: "number" },
							duration_ms: { type: "number" },
							os: { type: "string" },
							device: { type: "string" },
						},
						required: ["x", "y"],
					},
				},
				{
					name: "press_system_key",
					description:
						"Press a system key like home, back, enter, volume_up, volume_down.",
					inputSchema: {
						type: "object",
						properties: {
							key: { type: "string" },
							os: { type: "string" },
							device: { type: "string" },
						},
						required: ["key"],
					},
				},
				{
					name: "launch_application",
					description:
						"Launch an application by its package name or bundle ID.",
					inputSchema: {
						type: "object",
						properties: {
							app_id: { type: "string" },
							os: { type: "string" },
							device: { type: "string" },
						},
						required: ["app_id"],
					},
				},
				{
					name: "kill_application",
					description: "Kill an application by its package name or bundle ID.",
					inputSchema: {
						type: "object",
						properties: {
							app_id: { type: "string" },
							os: { type: "string" },
							device: { type: "string" },
						},
						required: ["app_id"],
					},
				},
			],
		};
	});

	server.setRequestHandler(CallToolRequestSchema, async (request) => {
		try {
			const args = request.params.arguments || {};
			const { queryService, actionService } = await getServices(
				args.os as string,
				args.device as string,
			);

			switch (request.params.name) {
				case "get_current_ui": {
					const ui = await queryService.getCurrentUI();
					return {
						content: [{ type: "text", text: JSON.stringify(ui) }],
					};
				}
				case "tap_coordinate": {
					await actionService.tapCoordinate(args.x as number, args.y as number);
					return { content: [{ type: "text", text: "Action successful" }] };
				}
				case "swipe_screen": {
					await actionService.swipeScreen(
						args.x1 as number,
						args.y1 as number,
						args.x2 as number,
						args.y2 as number,
						args.duration_ms as number,
					);
					return { content: [{ type: "text", text: "Action successful" }] };
				}
				case "input_text_field": {
					await actionService.inputTextField(args.text as string);
					return { content: [{ type: "text", text: "Action successful" }] };
				}
				case "long_press_coordinate": {
					await actionService.longPressCoordinate(
						args.x as number,
						args.y as number,
						args.duration_ms as number,
					);
					return { content: [{ type: "text", text: "Action successful" }] };
				}
				case "press_system_key": {
					await actionService.pressSystemKey(args.key as string);
					return { content: [{ type: "text", text: "Action successful" }] };
				}
				case "launch_application": {
					await actionService.launchApplication(args.app_id as string);
					return { content: [{ type: "text", text: "Action successful" }] };
				}
				case "kill_application": {
					await actionService.killApplication(args.app_id as string);
					return { content: [{ type: "text", text: "Action successful" }] };
				}
				default:
					throw new McpError(ErrorCode.MethodNotFound, "Unknown tool");
			}
		} catch (error: any) {
			return {
				content: [{ type: "text", text: `Action failed: ${error.message}` }],
				isError: true,
			};
		}
	});

	const transport = new StdioServerTransport();
	await server.connect(transport);
	console.error("AgenticADB MCP server running on stdio");
}

import { isMain } from "./is-main.js";

if (isMain(import.meta.url)) {
	runMcpServer(process.argv).catch((e) => {
		console.error(e);
		process.exit(1);
	});
}
