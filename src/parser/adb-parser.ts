import { XMLParser } from "fast-xml-parser";
import { ParseError } from "../client/base-client.js";
import { createUIElement, type UIElement } from "../models/ui-element.js";

export interface BaseParser {
	parse(data: string): UIElement[];
}

export class AdbParser implements BaseParser {
	parse(xmlData: string): UIElement[] {
		if (!xmlData || xmlData.trim() === "") {
			return [];
		}

		let cleanXml = xmlData;
		const xmlStart = xmlData.indexOf("<?xml");
		if (xmlStart > 0) {
			cleanXml = xmlData.substring(xmlStart);
		} else if (xmlStart === -1 && xmlData.includes("<hierarchy")) {
			const hierarchyStart = xmlData.indexOf("<hierarchy");
			cleanXml = xmlData.substring(hierarchyStart);
		}

		try {
			const parser = new XMLParser({
				ignoreAttributes: false,
				attributeNamePrefix: "@_",
				isArray: (name) => name === "node",
			});
			const parsed = parser.parse(cleanXml);

			if (!parsed || !parsed.hierarchy) {
				throw new ParseError("Invalid XML format");
			}

			const elements: UIElement[] = [];
			let index = 0;

			const traverse = (node: any) => {
				if (!node) return;

				if (node["@_class"]) {
					const rawClass = node["@_class"] as string;
					const classParts = rawClass.split(".");
					const className = classParts[classParts.length - 1];

					const rawId = node["@_resource-id"] || "";
					let id = rawId;
					if (rawId && rawId.includes("/")) {
						id = rawId.split("/")[1];
					}

					const text = node["@_text"] || "";
					const desc = node["@_content-desc"] || "";
					const clickable = node["@_clickable"] === "true";
					const bounds = node["@_bounds"] || "";

					let cx = 0;
					let cy = 0;
					let validBounds = false;
					const match = bounds.match(/\[(\d+),(\d+)\]\[(\d+),(\d+)\]/);
					if (match) {
						const x1 = parseInt(match[1], 10);
						const y1 = parseInt(match[2], 10);
						const x2 = parseInt(match[3], 10);
						const y2 = parseInt(match[4], 10);
						cx = Math.floor((x1 + x2) / 2);
						cy = Math.floor((y1 + y2) / 2);
						validBounds = true;
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
				}

				if (node.node) {
					const children = Array.isArray(node.node) ? node.node : [node.node];
					for (const child of children) {
						traverse(child);
					}
				}
			};

			traverse(parsed.hierarchy);
			return elements;
		} catch (e: any) {
			if (e instanceof ParseError) throw e;
			throw new ParseError(`Failed to parse Android UI XML: ${e.message}`);
		}
	}
}
