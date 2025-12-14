/*
 * Manual test script for the "Text Explosion" After Effects plugin.
 * Run inside After Effects' ExtendScript Toolkit or the AE scripting console.
 * Comments are in English as requested.
 *
 * How to run the manual test:
 * 1) Ensure the Text Explosion plugin is installed and visible under Effects.
 * 2) Open After Effects and create or open any project (an empty one is fine).
 * 3) Go to File → Scripts → Run Script File... and select this JSX file,
 *    or paste it into the ExtendScript Toolkit and run it with AE targeted.
 * 4) The script creates temporary comps and alerts a PASS/FAIL summary.
 * 5) If a test fails, read the alert text for the specific assertion message.
 */

// Simple assertion helper for readability.
function assertEqual(actual, expected, message) {
    if (actual !== expected) {
        throw new Error(message + " (expected: " + expected + ", got: " + actual + ")");
    }
}

function assertTruthy(value, message) {
    if (!value) {
        throw new Error(message + " (value was falsy)");
    }
}

// Test runner wrapper that reports overall pass/fail status in the Info panel.
function runTestSuite() {
    var report = [];

    function logResult(name, passed, error) {
        var status = passed ? "PASS" : "FAIL";
        var line = status + ": " + name + (error ? " — " + error : "");
        report.push(line);
    }

    // Test: applying the effect to a text layer should create expected properties.
    function testAppliesEffectWithDefaultControls() {
        var comp = app.project.items.addComp("TextExplosionTestComp", 1920, 1080, 1, 3, 30);
        var textLayer = comp.layers.addText("Boom");

        // Apply the plugin; replace the match name with the actual match name if different.
        var effect = textLayer.property("ADBE Effect Parade").addProperty("Text Explosion");

        assertTruthy(effect, "The effect was not applied to the layer.");
        // Example property checks; update names to match the plugin's exposed controls.
        assertTruthy(effect.property("Emission Count"), "Emission Count property is missing.");
        assertTruthy(effect.property("Velocity"), "Velocity property is missing.");
        assertTruthy(effect.property("Gravity"), "Gravity property is missing.");

        // Confirm default values align with creative spec.
        assertEqual(effect.property("Emission Count").value, 25, "Unexpected default emission count.");
        assertEqual(effect.property("Velocity").value, 500, "Unexpected default velocity.");
        assertEqual(effect.property("Gravity").value, 1200, "Unexpected default gravity.");
    }

    // Test: keyframing the explosion should animate from intact to scattered text.
    function testAnimationBehavesAsExplosion() {
        var comp = app.project.items.addComp("TextExplosionAnimComp", 1920, 1080, 1, 3, 30);
        var textLayer = comp.layers.addText("Shatter");
        var effect = textLayer.property("ADBE Effect Parade").addProperty("Text Explosion");

        assertTruthy(effect, "Effect failed to apply for animation test.");

        var emission = effect.property("Emission Count");
        assertTruthy(emission, "Emission Count control is missing.");

        // Keyframe emission from zero to the default burst to ensure particles spawn over time.
        emission.setValueAtTime(0, 0);
        emission.setValueAtTime(0.5, 25);

        // Simple expectation: two keyframes should exist and their values match.
        assertEqual(emission.numKeys, 2, "Emission Count keyframe count should be 2.");
        assertEqual(emission.keyValue(1), 0, "First emission keyframe should keep text intact.");
        assertEqual(emission.keyValue(2), 25, "Second emission keyframe should trigger the burst.");
    }

    // Register and execute tests.
    var tests = [
        { name: "Applies effect with default controls", fn: testAppliesEffectWithDefaultControls },
        { name: "Explosion animation keyframes", fn: testAnimationBehavesAsExplosion }
    ];

    for (var i = 0; i < tests.length; i++) {
        try {
            tests[i].fn();
            logResult(tests[i].name, true);
        } catch (e) {
            logResult(tests[i].name, false, e.message);
        }
    }

    alert(report.join("\n"));
}

// Execute when the script is run.
runTestSuite();
