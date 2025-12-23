# Resolve Yarn v3 Workspace Peer Dependency Conflicts

Your task is to resolve peer dependency conflicts in a Yarn v3 workspaces monorepo by aligning package version ranges across all workspace packages and regenerating a deterministic lock file. The solution must enable `yarn install --immutable` to succeed on Linux with Corepack enabled.

## Problem Description

The monorepo at `/app` uses Yarn v3 (Berry) with multiple workspace packages that have conflicting peer dependency requirements. Currently, `yarn install` fails due to unresolved peer dependency conflicts between workspace packages.

## Requirements

Your solution must:

1. **Enable Corepack** and configure it to use Yarn v3
2. **Align all peer dependency version ranges** across workspace packages in their respective `/app/packages/*/package.json` files to be compatible with each other
3. **Update the root `/app/package.json`** if necessary to enforce consistent dependency versions across workspaces
4. **Regenerate `/app/yarn.lock`** using Yarn v3 to create a deterministic lock file
5. **Ensure `yarn install --immutable` succeeds** without errors or warnings about peer dependencies on Linux
6. **Prove reproducibility** by demonstrating that two consecutive clean installs produce:
   - Identical resolved package versions in `/app/yarn.lock`
   - An unchanged `/app/.yarn/install-state.gz` file between the two installs

## Constraints

- Do not remove or skip any workspace packages
- Maintain the workspaces structure defined in `/app/package.json`
- Do not downgrade major versions of core dependencies below their current major version
- The solution must work with Corepack and Yarn v3 (Berry) on Linux
- All workspace packages must remain functional after dependency alignment

## Files

- Input: `/app/package.json` (root)
- Input: `/app/packages/*/package.json` (workspace packages)
- Input: `/app/yarn.lock` (existing, potentially broken)
- Output: Modified `/app/package.json` (if changes needed)
- Output: Modified `/app/packages/*/package.json` (with aligned dependencies)
- Output: Regenerated `/app/yarn.lock` (deterministic)
- Output: `/app/.yarn/install-state.gz` (must be reproducible)

## Success Criteria

1. `yarn install --immutable` runs successfully without errors
2. No peer dependency conflict warnings appear in the output
3. Two consecutive clean installs (with `node_modules` and `.yarn/cache` removed) produce identical lock files and install state
4. All workspace packages can still be built successfully after the fix
