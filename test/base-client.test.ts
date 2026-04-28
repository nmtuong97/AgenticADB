import * as child_process from "node:child_process";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { runCommand } from "../src/client/base-client.js";

vi.mock("node:child_process");

describe("BaseClient runCommand", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	it("should return stdout on success", async () => {
		const mockSpawn = vi.fn().mockImplementation(() => {
			const ee = new (require("events").EventEmitter)();
			ee.stdout = new (require("events").EventEmitter)();
			ee.stderr = new (require("events").EventEmitter)();

			setTimeout(() => {
				ee.stdout.emit("data", "success output");
				ee.emit("close", 0);
			}, 10);

			return ee;
		});

		(child_process.spawn as any) = mockSpawn;

		const result = await runCommand("echo", ["hello"]);
		expect(result).toBe("success output");
	});

	it("should throw CommandError on non-zero exit code", async () => {
		const mockSpawn = vi.fn().mockImplementation(() => {
			const ee = new (require("events").EventEmitter)();
			ee.stdout = new (require("events").EventEmitter)();
			ee.stderr = new (require("events").EventEmitter)();

			setTimeout(() => {
				ee.stderr.emit("data", "error output");
				ee.emit("close", 1);
			}, 10);

			return ee;
		});

		(child_process.spawn as any) = mockSpawn;

		await expect(runCommand("fail", [])).rejects.toThrow(
			/Command failed with code 1/,
		);
	});

	it("should retry if retry option is true", async () => {
		let attempts = 0;
		const mockSpawn = vi.fn().mockImplementation(() => {
			attempts++;
			const ee = new (require("events").EventEmitter)();
			ee.stdout = new (require("events").EventEmitter)();
			ee.stderr = new (require("events").EventEmitter)();

			setTimeout(() => {
				if (attempts < 2) {
					ee.emit("close", 1);
				} else {
					ee.stdout.emit("data", "success on retry");
					ee.emit("close", 0);
				}
			}, 10);

			return ee;
		});

		(child_process.spawn as any) = mockSpawn;

		const result = await runCommand("cmd", [], {
			retry: true,
			maxRetries: 2,
			backoffFactor: 0.001,
		});
		expect(result).toBe("success on retry");
		expect(attempts).toBe(2);
	});
});
