import type { BaseClient } from "../client/adb-client.js";
import type { UIElement } from "../models/ui-element.js";
import type { BaseParser } from "../parser/adb-parser.js";

export class UIQueryService {
	private cache: UIElement[] | null = null;

	constructor(
		private client: BaseClient,
		private parser: BaseParser,
	) {}

	clearCache() {
		this.cache = null;
	}

	async getCurrentUI(): Promise<UIElement[]> {
		if (this.cache) {
			return this.cache;
		}

		const rawOutput = await this.client.dumpUI();
		if (!rawOutput || rawOutput.trim() === "") {
			this.cache = [];
			return [];
		}

		const elements = this.parser.parse(rawOutput);
		this.cache = elements;
		return elements;
	}
}
