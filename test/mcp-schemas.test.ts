import { describe, expect, it } from "vitest";
import * as schemas from "../src/schemas/mcp-schemas.js";

describe("MCP Schemas", () => {
	it("should parse getUiSchema with no args", () => {
		const result = schemas.getUiSchema.parse({});
		expect(result).toEqual({});
	});

	it("should parse tapCoordinateSchema with valid args", () => {
		const result = schemas.tapCoordinateSchema.parse({ x: 10, y: 20 });
		expect(result).toEqual({ x: 10, y: 20 });
	});

	it("should fail tapCoordinateSchema with invalid args", () => {
		expect(() =>
			schemas.tapCoordinateSchema.parse({ x: "10", y: 20 }),
		).toThrow();
		expect(() =>
			schemas.tapCoordinateSchema.parse({ x: -10, y: 20 }),
		).toThrow();
	});

	it("should parse swipeScreenSchema with valid args and default duration", () => {
		const result = schemas.swipeScreenSchema.parse({
			x1: 10,
			y1: 20,
			x2: 30,
			y2: 40,
		});
		expect(result).toEqual({
			x1: 10,
			y1: 20,
			x2: 30,
			y2: 40,
			duration_ms: 300,
		});
	});

	it("should parse inputTextFieldSchema", () => {
		const result = schemas.inputTextFieldSchema.parse({ text: "hello" });
		expect(result).toEqual({ text: "hello" });
	});
});
