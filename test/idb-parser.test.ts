import * as fs from "node:fs";
import * as path from "node:path";
import { describe, expect, it } from "vitest";
import { IdbParser } from "../src/parser/idb-parser.js";

describe("IdbParser", () => {
	it("should parse valid json and filter noise", () => {
		const parser = new IdbParser();
		const jsonPath = path.resolve(__dirname, "fixtures/mock_ios_dump.json");

		if (!fs.existsSync(jsonPath)) {
			throw new Error(`Fixture not found: ${jsonPath}`);
		}

		const json = fs.readFileSync(jsonPath, "utf8");
		const result = parser.parse(json);

		expect(result).toBeInstanceOf(Array);
		expect(result.length).toBeGreaterThan(0);

		const el = result[0];
		expect(el).toHaveProperty("index");
		expect(el).toHaveProperty("class");
		expect(el).toHaveProperty("text");
		expect(el).toHaveProperty("id");
		expect(el).toHaveProperty("desc");
		expect(el).toHaveProperty("clickable");
		expect(el).toHaveProperty("center_x");
		expect(el).toHaveProperty("center_y");

		expect(typeof el.center_x).toBe("number");
		expect(Number.isInteger(el.center_x)).toBe(true);
	});

	it("should return empty array for empty input", () => {
		const parser = new IdbParser();
		expect(parser.parse("")).toEqual([]);
		expect(parser.parse("   ")).toEqual([]);
	});

	it("should compute center_x and center_y correctly from frame", () => {
		const parser = new IdbParser();
		const json = JSON.stringify({
			type: "XCUIElementTypeButton",
			AXValue: "Submit",
			AXLabel: "Submit Button",
			AXIdentifier: "btn_submit",
			traits: ["button"],
			frame: {
				x: 100,
				y: 200,
				width: 200,
				height: 100,
			},
		});

		const result = parser.parse(json);
		expect(result.length).toBe(1);
		const el = result[0];

		expect(el.center_x).toBe(200);
		expect(el.center_y).toBe(250);
		expect(el.text).toBe("Submit");
		expect(el.class).toBe("Button");
		expect(el.id).toBe("btn_submit");
		expect(el.clickable).toBe(true);
	});

	it("should gracefully extract JSON from noisy output", () => {
		const parser = new IdbParser();
		const noisyInput = `
Warning: some idb daemon message here.
Connecting to device...
{"type":"XCUIElementTypeButton","AXLabel":"NoisyButton","frame":{"x":10,"y":20,"width":30,"height":40}}
Finished dumping.
		`;
		const elements = parser.parse(noisyInput);
		expect(elements.length).toBe(1);
		expect(elements[0].desc).toBe("NoisyButton");
		expect(elements[0].center_x).toBe(10 + 15);
		expect(elements[0].center_y).toBe(20 + 20);
	});
});
