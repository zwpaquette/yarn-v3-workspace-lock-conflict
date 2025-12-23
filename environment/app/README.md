# Yarn v3 Monorepo

This is a Yarn v3 workspaces monorepo with intentionally conflicting peer dependencies.

## Problem

- `ui-lib` requires React ^17.0.0
- `dashboard` requires React ^18.0.0
- `analytics` requires React >=18.0.0

These version ranges are incompatible and will cause `yarn install` to fail.

## Workspace Structure

```
packages/
  ui-lib/       - UI component library (React 17)
  dashboard/    - Dashboard app (React 18)
  analytics/    - Analytics module (React 18)
```
