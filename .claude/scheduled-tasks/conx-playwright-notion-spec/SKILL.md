---
name: conx-playwright-notion-spec
description: หา Notion task "Wait test pr" แล้วเขียน Playwright spec ให้
---

You are a QA automation engineer. Your goal is to find ONE Notion task that needs a Playwright test and write it.

## Repos
- conx-playwright: https://github.com/xinexo/conx-playwright (clone and work here)
- connect-x-front: https://github.com/xinexo/connect-x-front (read-only, for locators)

## Steps

### 1. Find the task in Notion
- Use Notion MCP (notion-search) to find tasks where:
  - Title starts with "frontend" (case-insensitive)
  - Status property is "Wait test pr" (or similar waiting/testing status)
- If multiple results, pick the most recent one
- If no results found → stop and report "No tasks found with status Wait test pr"

### 2. Read the task
- Use notion-fetch to read the full page content
- Identify: which feature/page needs testing, what changed in this task
- Note the task title and Notion page ID

### 3. Find the feature in connect-x-front
- Clone connect-x-front repo
- Go to src/feature/<FeatureName>/ based on task description
- Read .tsx files to find: id= attributes, route URL (also check src/stores/route.ts), button text, breadcrumb text

### 4. Read conventions
- Read conx-playwright/PLAYWRIGHT_CONVENTIONS.md

### 5. Write spec file
- Create tests/<feature-name>.spec.ts with at least 3 test cases:
  - TC-01: page loads, breadcrumb correct
  - TC-02: key UI element visible
  - TC-03: one navigation or interaction
- Every test MUST:
  - test.setTimeout(2 * 60 * 1000) as first line
  - Login Block: doLogin(page, { force: false }) + ensureStorageState(page)
  - waitUntil: 'domcontentloaded'
  - id= selectors from actual frontend code

### 6. Update suite-map.json
- Add spec to "full" suite array
- Add pattern: "src/feature/<FeatureName>/**": ["tests/<feature>.spec.ts"]

### 7. Commit and push
- Stage only: tests/<feature>.spec.ts and suite-map.json
- Do NOT commit: .env, auth/, node_modules
- Set E2E_BASE_URL=https://app.connect-x.tech in .env
- Commit: "add <feature> spec from Notion task <task-title>"
- Push to branch develop on conx-playwright

### 8. Comment on Notion task
- Use notion-create-comment to add comment on the task page:
  "Playwright test written and pushed to conx-playwright develop branch. Spec: tests/<feature>.spec.ts — Commit: <hash>"

### 9. Report
- Notion task: title + URL
- Feature tested + URL path
- Test cases written
- Commit hash

## Rules
- If spec already exists for this feature, skip to next task
- Do not run tests (no browser)
- Only process ONE task per run