export interface UIElement {
	index: number;
	class: string;
	text: string;
	id: string;
	desc: string;
	clickable: boolean;
	center_x: number;
	center_y: number;
}

export function createUIElement(data: Partial<UIElement>): UIElement {
	let cx = data.center_x ?? 0;
	let cy = data.center_y ?? 0;
	if (cx < 0) cx = 0;
	if (cy < 0) cy = 0;

	return {
		index: data.index ?? 0,
		class: data.class ?? "",
		text: data.text ?? "",
		id: data.id ?? "",
		desc: data.desc ?? "",
		clickable: data.clickable ?? false,
		center_x: Math.floor(cx),
		center_y: Math.floor(cy),
	};
}
