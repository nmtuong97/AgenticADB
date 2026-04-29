import type { BaseClient } from "../client/adb-client.js";
import type { UIElement } from "../models/ui-element.js";
import type { BaseParser } from "../parser/adb-parser.js";

export class UIQueryService {
	constructor(
		private client: BaseClient,
		private parser: BaseParser,
	) {}

	async getCurrentUI(): Promise<UIElement[]> {
		const rawOutput = await this.client.dumpUI();
		if (!rawOutput || rawOutput.trim() === "") {
			return [];
		}

		return this.parser.parse(rawOutput);
	}
}
