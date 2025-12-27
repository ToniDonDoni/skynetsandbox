const fs = require('fs');
const path = require('path');
const vm = require('vm');

const jsxPath = path.join(__dirname, '..', 'src', 'plugins', 'textExplosionPlugin.jsx');
const source = fs.readFileSync(jsxPath, 'utf8');

try {
  // Compiles the script without executing it to ensure valid ExtendScript-compatible syntax.
  new vm.Script(source, { filename: jsxPath });
  console.log(`Syntax check passed for ${jsxPath}`);
} catch (error) {
  console.error(`Syntax check failed for ${jsxPath}:\n${error.message}`);
  process.exitCode = 1;
}
