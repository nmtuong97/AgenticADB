import { ParseError } from "../client/base-client.js";
import { createUIElement, type UIElement } from "../models/ui-element.js";
import type { BaseParser } from "./adb-parser.js";

export class IdbParser implements BaseParser {
	parse(jsonData: string): UIElement[] {
		if (!jsonData || jsonData.trim() === "") {
			return [];
		}

		try {
			// Extract valid JSON substring to bypass plain-text prefixes/suffixes
			let cleanedData = jsonData;
			const firstBrace = jsonData.indexOf("{");
			const firstBracket = jsonData.indexOf("[");
			const firstIndex =
				firstBrace === -1
					? firstBracket
					: firstBracket === -1
						? firstBrace
						: Math.min(firstBrace, firstBracket);

			if (firstIndex !== -1) {
				const isArray = firstIndex === firstBracket;
				const lastIndex = isArray
					? jsonData.lastIndexOf("]")
					: jsonData.lastIndexOf("}");
				if (lastIndex !== -1 && lastIndex >= firstIndex) {
					cleanedData = jsonData.substring(firstIndex, lastIndex + 1);
				}
			}

			const parsed = JSON.parse(cleanedData);
			const elements: UIElement[] = [];
			let index = 0;

			const traverse = (node: any) => {
				if (!node) return;

				const rawType = node.type || "";
				const className = rawType.replace("XCUIElementType", "");

				const text = node.AXValue || node.title || "";
				const desc = node.AXLabel || "";
				const id = node.AXIdentifier || "";

				const traits = Array.isArray(node.AXTraits)
					? node.AXTraits
					: node.traits || [];
				const clickable =
					traits.includes("button") ||
					traits.includes("link") ||
					traits.includes("plays_sound") ||
					traits.includes("keyboard_key");

				let cx = 0;
				let cy = 0;
				let validBounds = false;

				const frame = node.frame;
				if (frame && typeof frame === "object") {
					const x = frame.x;
					const y = frame.y;
					const w = frame.width;
					const h = frame.height;

					if (x != null && y != null && w != null && h != null) {
						cx = Math.floor(x + w / 2);
						cy = Math.floor(y + h / 2);
						validBounds = true;
					}
				}

				if (text || desc || id || clickable) {
					elements.push(
						createUIElement({
							index: index++,
							class: className,
							text,
							id,
							desc,
							clickable,
							center_x: validBounds ? cx : 0,
							center_y: validBounds ? cy : 0,
						}),
					);
				}

				const children = node.children || [];
				for (const child of children) {
					traverse(child);
				}
			};

			traverse(parsed);
			return elements;
		} catch (e: any) {
			throw new ParseError(`Failed to parse iOS UI JSON: ${e.message}`);
		}
	}
}
