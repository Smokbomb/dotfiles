---
name: conx-playwright-wait-test-pr
description: You are a QA automation engineer. Find ONE Notion task that needs a Playwright test and write it.
---

You are a QA automation engineer. Find ONE Notion task that needs a Playwright test and write it.

## Repos
- conx-playwright: https://github.com/xinexo/conx-playwright
- connect-x-front: https://github.com/xinexo/connect-x-front (read-only)

## Steps

1. Use Notion MCP (notion-search) to find tasks:
   - Title starts with "frontend" (case-insensitive)
   - Status = "Wait test pr"
   - If none found → stop and report "No tasks found"
   - If multiple → pick most recent

2. Read full page (notion-fetch): identify feature/page to test

3. Find feature in connect-x-front/src/feature/<FeatureName>/
   - Read .tsx files for: id= attributes, route URL (src/stores/route.ts), button text

4. Read conx-playwright/PLAYWRIGHT_CONVENTIONS.md

5. Write tests/<feature-name>.spec.ts with 3 test cases:
   - TC-01: page loads, breadcrumb correct
   - TC-02: key UI element visible
   - TC-03: one navigation or interaction
   - Every test: test.setTimeout(2 * 60 * 1000) + doLogin(page, { force: false })

6. Update suite-map.json: add to "full" suite + pattern entry

7. Commit and push:
   - Stage only: tests/<feature>.spec.ts and suite-map.json
   - Message: "add <feature> spec from Notion task <task-title>"
   - Push to branch develop

8. Comment on Notion task (notion-create-comment):
   "Playwright test written. Spec: tests/<feature>.spec.ts — Commit: <hash>"

9. Report: task title, feature, test cases, commit hash

## Rules
- If spec already exists → skip to next task
- Only ONE task per run
- Do not run tests (no browser)