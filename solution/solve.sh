#!/bin/bash
# CANARY_STRING_PLACEHOLDER

set -e  # Exit immediately if any command fails

echo "=========================================="
echo "Resolving Yarn v3 Workspace Peer Dependencies"
echo "=========================================="

# Step 1: Navigate to the app directory
cd /app

# Step 2: Enable Corepack and set Yarn version
echo "Step 1: Enabling Corepack and setting Yarn v3..."
corepack enable
corepack prepare yarn@3.6.4 --activate

# Step 3: Analyze the conflict
echo "Step 2: Analyzing peer dependency conflicts..."
echo "Current state:"
echo "  - ui-lib requires React ^17.0.2"
echo "  - dashboard requires React ^18.2.0"
echo "  - analytics requires React ^18.3.0"
echo "Solution: Align all packages to React 18.x"

# Step 4: Update ui-lib to use React 18 (align with other packages)
echo "Step 3: Updating ui-lib to React 18..."
node << 'EOF'
const fs = require('fs');
const path = '/app/packages/ui-lib/package.json';
const pkg = JSON.parse(fs.readFileSync(path, 'utf8'));

// Update to React 18 to match dashboard and analytics
pkg.dependencies.react = '^18.2.0';
pkg.peerDependencies.react = '^18.0.0';

fs.writeFileSync(path, JSON.stringify(pkg, null, 2) + '\n');
console.log('Updated ui-lib to React ^18.2.0');
EOF

# Step 5: Update dashboard to align peer dependencies
echo "Step 4: Aligning dashboard peer dependencies..."
node << 'EOF'
const fs = require('fs');
const path = '/app/packages/dashboard/package.json';
const pkg = JSON.parse(fs.readFileSync(path, 'utf8'));

// Ensure consistent React 18 version
pkg.dependencies.react = '^18.2.0';
pkg.peerDependencies.react = '^18.0.0';

fs.writeFileSync(path, JSON.stringify(pkg, null, 2) + '\n');
console.log('Updated dashboard peer dependencies');
EOF

# Step 6: Update analytics to align with the same React version
echo "Step 5: Aligning analytics dependencies..."
node << 'EOF'
const fs = require('fs');
const path = '/app/packages/analytics/package.json';
const pkg = JSON.parse(fs.readFileSync(path, 'utf8'));

// Align to same React version as other packages
pkg.dependencies.react = '^18.2.0';
pkg.peerDependencies.react = '^18.0.0';

fs.writeFileSync(path, JSON.stringify(pkg, null, 2) + '\n');
console.log('Updated analytics to React ^18.2.0');
EOF

# Step 7: Add resolutions to root package.json to enforce single React version
echo "Step 6: Adding resolutions to root package.json..."
node << 'EOF'
const fs = require('fs');
const path = '/app/package.json';
const pkg = JSON.parse(fs.readFileSync(path, 'utf8'));

// Add resolutions to enforce React 18 across all workspaces
pkg.resolutions = {
  "react": "18.2.0",
  "react-dom": "18.2.0"
};

fs.writeFileSync(path, JSON.stringify(pkg, null, 2) + '\n');
console.log('Added resolutions to root package.json');
EOF

# Step 8: Remove old node_modules and lock file to start fresh
echo "Step 7: Cleaning old dependencies..."
rm -rf /app/node_modules
rm -rf /app/packages/*/node_modules
rm -rf /app/.yarn/cache
rm -rf /app/.yarn/install-state.gz
rm -f /app/yarn.lock

# Step 9: Install dependencies with Yarn v3
echo "Step 8: Installing dependencies with Yarn v3..."
yarn install

# Step 10: Verify installation works with --immutable flag
echo "Step 9: Testing immutable install..."
rm -rf /app/node_modules
rm -rf /app/packages/*/node_modules
rm -rf /app/.yarn/cache
rm -rf /app/.yarn/install-state.gz

yarn install --immutable

# Step 11: Prove reproducibility - do a second clean install
echo "Step 10: Proving reproducibility with second clean install..."

# Save first install state
cp /app/yarn.lock /tmp/yarn.lock.first
cp /app/.yarn/install-state.gz /tmp/install-state.first.gz

# Clean and reinstall
rm -rf /app/node_modules
rm -rf /app/packages/*/node_modules
rm -rf /app/.yarn/cache
rm -rf /app/.yarn/install-state.gz

yarn install --immutable

# Compare lock files
echo "Step 11: Verifying reproducibility..."
if diff /app/yarn.lock /tmp/yarn.lock.first > /dev/null; then
    echo "✓ yarn.lock is identical after reinstall"
else
    echo "✗ yarn.lock differs - NOT REPRODUCIBLE"
    exit 1
fi

# Compare install states
if cmp -s /app/.yarn/install-state.gz /tmp/install-state.first.gz; then
    echo "✓ install-state.gz is identical after reinstall"
else
    echo "✗ install-state.gz differs - NOT REPRODUCIBLE"
    exit 1
fi

echo "=========================================="
echo "✓ Task completed successfully!"
echo "✓ All peer dependencies resolved"
echo "✓ yarn install --immutable succeeds"
echo "✓ Reproducibility proven"
echo "=========================================="
