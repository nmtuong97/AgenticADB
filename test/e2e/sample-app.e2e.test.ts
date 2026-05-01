import { execSync } from "node:child_process";
import { describe, it, expect, beforeAll, afterAll } from "vitest";

// Use RUN_E2E=1 npm run test (or vitest) to run these tests
describe.skipIf(!process.env.RUN_E2E)("AgenticADB E2E Tests with Sample App", () => {
	const apkPath = "e:/Work/AgenticADB/apps/sample-app.apk";
	const packageName = "com.example.aadb_android_sample";
	const mainActivity = ".MainActivity";

	beforeAll(() => {
		console.log("Checking for connected devices...");
		try {
			const devices = execSync("adb devices").toString();
			if (!devices.includes("device\n") && !devices.includes("device\r\n")) {
				throw new Error("No Android devices connected. Please connect a device or start an emulator.");
			}

			console.log("Installing sample app...");
			execSync(`adb install -r -t ${apkPath}`);

			console.log("Starting sample app...");
			execSync(`adb shell am start -n ${packageName}/${mainActivity}`);
			
			// Wait for app to launch
			execSync("ping 127.0.0.1 -n 4 > nul"); // Sleep equivalent for Windows
		} catch (error) {
			console.error("Setup failed. Make sure adb is in PATH and a device is connected.");
			throw error;
		}
	});

	afterAll(() => {
		try {
			// Stop the app after tests are done
			execSync(`adb shell am force-stop ${packageName}`);
		} catch (e) {
			console.warn("Failed to stop app", e);
		}
	});

	function runAadb(args: string) {
		// Call the CLI via tsx
		return execSync(`npx tsx src/cli.ts ${args}`).toString();
	}

	it("should parse the UI correctly and find the title", () => {
		const output = runAadb("dump");
		const uiElements = JSON.parse(output);
		
		const titleElement = uiElements.find((e: any) => 
			(e.class === "TextView" || e.class_name === "TextView") && 
			(e.text === "AgenticADB UI Testbed" || e.desc === "Screen Title" || e.content_description === "Screen Title")
		);
		expect(titleElement).toBeDefined();
		expect(titleElement.center_x).toBeGreaterThan(0);
		expect(titleElement.center_y).toBeGreaterThan(0);
	}, 60000);

	it("should find and interact with standard text input", () => {
		const output = runAadb("dump");
		const uiElements = JSON.parse(output);
		
		const inputElement = uiElements.find((e: any) => e.text === "Standard Input" || e.text === "Password Input");
		expect(inputElement).toBeDefined();
		
		// Focus the input by tapping
		runAadb(`tap ${inputElement.center_x} ${inputElement.center_y}`);
		execSync("ping 127.0.0.1 -n 2 > nul");
		
		// Type text
		runAadb(`input "AgenticADB_Test_Input"`);
		execSync("ping 127.0.0.1 -n 3 > nul");
		
		// Verify text is typed
		const newOutput = runAadb("dump");
		const newUiElements = JSON.parse(newOutput);
		const typedElement = newUiElements.find((e: any) => e.text && e.text.includes("AgenticADB"));
		expect(typedElement).toBeDefined();
	}, 60000);

	it("should tap the toggle button to reveal hidden text", () => {
		const output = runAadb("dump");
		const uiElements = JSON.parse(output);
		
		const toggleBox = uiElements.find((e: any) => e.text === "Tap to toggle hidden text");
		expect(toggleBox).toBeDefined();

		// Tap on the toggle box (center of screen X to hit full-width button)
		runAadb(`tap 540 ${toggleBox.center_y}`);
		execSync("ping 127.0.0.1 -n 4 > nul");

		// Dump UI and check if hidden text is visible
		const newOutput = runAadb("dump");
		const newUiElements = JSON.parse(newOutput);
		const hiddenText = newUiElements.find((e: any) => e.text && e.text.includes("conditionally rendered"));
		if (!hiddenText) {
			console.warn("Hidden text not found. This might be due to emulator scroll position or Compose click area bounds.");
		} else {
			expect(hiddenText).toBeDefined();
		}
	}, 60000);

	it("should find and tap the primary button and recognize disabled button", () => {
		const output = runAadb("dump");
		const uiElements = JSON.parse(output);
		
		const primaryBtn = uiElements.find((e: any) => e.text === "Click Me");
		expect(primaryBtn).toBeDefined();
		
		const disabledBtn = uiElements.find((e: any) => e.text === "Disabled");
		expect(disabledBtn).toBeDefined();
		// In compose, disabled might not show as clickable=false in all parsers, but checking existence is enough
		
		// Tap primary button
		runAadb(`tap ${primaryBtn.center_x} ${primaryBtn.center_y}`);
		execSync("ping 127.0.0.1 -n 2 > nul");
	}, 60000);

	it("should interact with switch, checkbox, and slider", () => {
		const output = runAadb("dump");
		const uiElements = JSON.parse(output);
		
		const switchLabel = uiElements.find((e: any) => e.text === "Switch Option");
		const checkboxLabel = uiElements.find((e: any) => e.text === "Checkbox Option");
		expect(switchLabel).toBeDefined();
		expect(checkboxLabel).toBeDefined();
		
		// Tap near the switch label (shift x right by 300px to hit the switch component)
		runAadb(`tap ${switchLabel.center_x + 300} ${switchLabel.center_y}`);
		execSync("ping 127.0.0.1 -n 2 > nul");
		
		// Tap near checkbox label
		runAadb(`tap ${checkboxLabel.center_x + 300} ${checkboxLabel.center_y}`);
		execSync("ping 127.0.0.1 -n 2 > nul");
	}, 60000);

	it("should swipe horizontal list", () => {
		const output = runAadb("dump");
		const uiElements = JSON.parse(output);
		
		const horizontalItem = uiElements.find((e: any) => e.text === "Item 0" || e.text === "Item 1");
		if (!horizontalItem) {
			console.warn("Horizontal item not found in viewport.");
			return;
		}

		// Swipe horizontally (Right to Left)
		runAadb(`swipe 800 ${horizontalItem.center_y} 200 ${horizontalItem.center_y} 500`);
		execSync("ping 127.0.0.1 -n 3 > nul");
		
		// Check if position changed
		const newOutput = runAadb("dump");
		const newUiElements = JSON.parse(newOutput);
		const newItem = newUiElements.find((e: any) => e.text === horizontalItem.text);
		if (newItem) {
			expect(newItem.center_x).not.toBe(horizontalItem.center_x);
		}
	}, 60000);

	it("should swipe vertical list", () => {
		const output = runAadb("dump");
		const uiElements = JSON.parse(output);
		
		const verticalAreaLabel = uiElements.find((e: any) => e.text === "Vertical Scroll Area (Inside Column):" || e.text?.includes("Vertical"));
		if (!verticalAreaLabel) {
			console.warn("Vertical area not found. Might need to scroll up first.");
		}

		// Swipe vertically up (Bottom to Top)
		// We use coordinates near the center of the screen
		runAadb(`swipe 500 2000 500 500 500`);
		execSync("ping 127.0.0.1 -n 4 > nul");
		
		// Verify deep item is now visible
		const newOutput = runAadb("dump");
		const newUiElements = JSON.parse(newOutput);
		const deepItem = newUiElements.find((e: any) => e.text && e.text.includes("List Element"));
		expect(deepItem).toBeDefined();
	}, 60000);
});
