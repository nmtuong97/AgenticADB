import { describe, expect, it } from "vitest";
import { createUIElement } from "../src/models/ui-element.js";

describe("UIElement", () => {
	it("should initialize with provided values", () => {
		const el = createUIElement({
			index: 1,
			class: "Button",
			text: "Submit",
			id: "btn_submit",
			desc: "Submit Button",
			clickable: true,
			center_x: 100,
			center_y: 200,
		});

		expect(el.index).toBe(1);
		expect(el.class).toBe("Button");
		expect(el.text).toBe("Submit");
		expect(el.id).toBe("btn_submit");
		expect(el.desc).toBe("Submit Button");
		expect(el.clickable).toBe(true);
		expect(el.center_x).toBe(100);
		expect(el.center_y).toBe(200);
	});

	it("should normalize missing values", () => {
		const el = createUIElement({});
		expect(el.index).toBe(0);
		expect(el.class).toBe("");
		expect(el.text).toBe("");
		expect(el.id).toBe("");
		expect(el.desc).toBe("");
		expect(el.clickable).toBe(false);
		expect(el.center_x).toBe(0);
		expect(el.center_y).toBe(0);
	});

	it("should normalize negative coordinates to 0", () => {
		const el = createUIElement({ center_x: -10, center_y: -20 });
		expect(el.center_x).toBe(0);
		expect(el.center_y).toBe(0);
	});

	it("should floor floating point coordinates", () => {
		const el = createUIElement({ center_x: 10.5, center_y: 20.9 });
		expect(el.center_x).toBe(10);
		expect(el.center_y).toBe(20);
	});
});
