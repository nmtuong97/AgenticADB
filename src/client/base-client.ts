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

				child.on("close", (code: any, signal: any) => {
					if (code !== 0 || signal) {
						let errorMessage = `Command failed`;
						if (code !== null) errorMessage += ` with code ${code}`;
						if (signal != null) errorMessage += ` (killed by signal ${signal})`;
						if (stderr.trim()) errorMessage += `: ${stderr.trim()}`;
						reject(new CommandError(errorMessage));
					} else {
						resolve(stdout);
					}
				});
			});
		} catch (error: any) {
			if (!retry || attempt >= maxRetries) {
				if (error instanceof CommandError) {
					const isTimeout =
						error.message.includes("signal SIGTERM") ||
						error.message.includes("signal SIGKILL");
					if (isTimeout) {
						throw new CommandError(
							`Command timed out after ${timeout}ms. ${error.message}`,
						);
					}
				}
				throw error;
			}
			attempt++;
			const delay = Math.min(1000 * backoffFactor ** attempt, 30000);
			await new Promise((resolve) => setTimeout(resolve, delay));
		}
	}
	throw new CommandError("Command failed after all retry attempts");
}
