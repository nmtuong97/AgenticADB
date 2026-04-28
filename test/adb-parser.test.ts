import * as fs from "node:fs";
import * as path from "node:path";
import { describe, expect, it } from "vitest";
import { AdbParser } from "../src/parser/adb-parser.js";

describe("AdbParser", () => {
	it("should parse valid xml and filter noise", () => {
		const parser = new AdbParser();
		const xmlPath = path.resolve(__dirname, "fixtures/mock_android_dump.xml");

		if (fs.existsSync(xmlPath)) {
			const xml = fs.readFileSync(xmlPath, "utf8");
			const result = parser.parse(xml);

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
		} else {
			console.warn("Skipping fixture test: mock_android_dump.xml not found");
		}
	});

	it("should return empty array for empty input", () => {
		const parser = new AdbParser();
		expect(parser.parse("")).toEqual([]);
		expect(parser.parse("   ")).toEqual([]);
	});

	it("should compute center_x and center_y correctly from bounds", () => {
		const parser = new AdbParser();
		const xml = `<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="Click me" resource-id="com.example:id/btn" class="android.widget.Button" package="com.example" content-desc="A button" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[100,200][300,400]" />
</hierarchy>`;

		const result = parser.parse(xml);
		expect(result.length).toBe(1);
		const el = result[0];

		expect(el.center_x).toBe(200);
		expect(el.center_y).toBe(300);
		expect(el.text).toBe("Click me");
		expect(el.id).toBe("btn");
		expect(el.class).toBe("Button");
	});
});
