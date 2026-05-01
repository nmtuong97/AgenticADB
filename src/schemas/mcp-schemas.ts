import { z } from "zod";

export const getUiSchema = z.object({
	os: z.string().optional(),
	device: z.string().optional(),
});

export const tapCoordinateSchema = z.object({
	x: z.number().int().min(0),
	y: z.number().int().min(0),
	os: z.string().optional(),
	device: z.string().optional(),
});

export const swipeScreenSchema = z.object({
	x1: z.number().int().min(0),
	y1: z.number().int().min(0),
	x2: z.number().int().min(0),
	y2: z.number().int().min(0),
	duration_ms: z.number().int().min(0).optional().default(300),
	os: z.string().optional(),
	device: z.string().optional(),
});

export const inputTextFieldSchema = z.object({
	text: z.string(),
	os: z.string().optional(),
	device: z.string().optional(),
});

export const longPressCoordinateSchema = z.object({
	x: z.number().int().min(0),
	y: z.number().int().min(0),
	duration_ms: z.number().int().min(0).optional().default(1000),
	os: z.string().optional(),
	device: z.string().optional(),
});

export const pressSystemKeySchema = z.object({
	key: z.string(),
	os: z.string().optional(),
	device: z.string().optional(),
});

export const launchApplicationSchema = z.object({
	app_id: z.string(),
	os: z.string().optional(),
	device: z.string().optional(),
});

export const killApplicationSchema = z.object({
	app_id: z.string(),
	os: z.string().optional(),
	device: z.string().optional(),
});
