import { spawn } from "node:child_process";

export class CommandError extends Error {
	constructor(message: string) {
		super(message);
		this.name = "CommandError";
	}
}

export class ParseError extends Error {
	constructor(message: string) {
		super(message);
		this.name = "ParseError";
	}
}

export class DeviceNotFoundError extends Error {
	constructor(message: string) {
		super(message);
		this.name = "DeviceNotFoundError";
	}
}

export class AgenticADBError extends Error {
	constructor(message: string) {
		super(message);
		this.name = "AgenticADBError";
	}
}

export async function runCommand(
	cmd: string,
	args: string[],
	options: {
		timeout?: number;
		retry?: boolean;
		maxRetries?: number;
		backoffFactor?: number;
	} = {},
): Promise<string> {
	const {
		timeout = 10000,
		retry = false,
		maxRetries = 3,
		backoffFactor = 2,
	} = options;
	let attempt = 0;

	while (attempt <= (retry ? maxRetries : 0)) {
		try {
			return await new Promise((resolve, reject) => {
				let stdout = "";
				let stderr = "";

				const child = spawn(cmd, args, { timeout });

				child.stdout.on("data", (data: any) => {
					stdout += data.toString();
				});

				child.stderr.on("data", (data: any) => {
					stderr += data.toString();
				});

				child.on("error", (err: any) => {
					reject(
						new CommandError(`Failed to start subprocess: ${err.message}`),
					);
				});

				child.on("close", (code: any) => {
					if (code !== 0) {
						reject(
							new CommandError(`Command failed with code ${code}: ${stderr}`),
						);
					} else {
						resolve(stdout);
					}
				});
			});
		} catch (error) {
			if (!retry || attempt >= maxRetries) {
				throw error;
			}
			attempt++;
			const delay = Math.min(1000 * backoffFactor ** attempt, 30000);
			await new Promise((resolve) => setTimeout(resolve, delay));
		}
	}
	throw new CommandError("Command failed");
}
