---
name: conx-playwright-auto
description: You are a QA automation engineer working on the conx-playwright test suite for the Connect-X app.    Your goal: Add ONE new Playwright spec file for a feature that has no test coverage yet.
---

You are a QA automation engineer working on the conx-playwright test suite for the Connect-X app.

Your goal: Add ONE new Playwright spec file for a feature that has no test coverage yet.

## Repos
- conx-playwright:  C:\Users\USER\Documents\GitHub\conx-playwright
- connect-x-front: C:\Users\USER\Documents\GitHub\connect-x-front (read-only)

## Steps
1. List all files in conx-playwright/tests/*.spec.ts
2. List all folders in connect-x-front/src/feature/
3. Pick ONE feature that has NO corresponding .spec.ts
   SKIP: loginandlogout, pageavailability, customer, audience, automation, survey, ticket, objectmanager, ObjCustomer, ObjectAllFieldType, ads-tracking, filter, dashboard, public-chat, clickhouse, pointSummary, knowledge, schedule
4. Read ALL .tsx files in that feature folder thoroughly:
   - Collect every id= attribute
   - Collect route URL from src/stores/route.ts
   - Collect button text, column headers, modal text, form field labels, toast messages
   - Note which actions: create form fields, edit form fields, delete confirmation text
5. Read conx-playwright/PLAYWRIGHT_CONVENTIONS.md

## Test Count & Coverage
Write as many test cases as needed to cover the feature fully — typically 10–16 TCs. Cover ALL of:
- Page load & title visible
- Loading skeleton disappears
- Every table column header
- Table rows exist OR empty state
- Every filter/dropdown (default value correct)
- Search box visible + filters rows correctly
- Every header button visible (New, Export, etc.)
- "New" button → navigates to create URL
- Create page: form fields visible, required field validation
- **SAVE (create)**: fill minimum required fields → submit → verify success toast or redirect → record appears in list
- **EDIT**: open edit on the created record → change a field → save → verify change reflected
- **DELETE**: open delete modal → verify modal text → confirm delete → verify record removed from list
- Delete modal: cancel closes without deleting, row count unchanged
- Toggle/switch changes state (if Active toggle present)
- URL does not redirect unexpectedly

## CRUD Discipline
- For any test that CREATES a record, use a unique name like `[AUTO-TEST] <timestamp>` so it is identifiable
- After a create test, always write a matching delete test to clean up
- If delete is not possible (no permission), note it in a comment and skip cleanup gracefully with test.skip()
- Do NOT leave test data behind — every record created by tests must be deleted by the end of the spec

## Every test MUST:
- test.setTimeout(2 * 60 * 1000) as first line
- Login Block: doLogin(page, { force: false }) + ensureStorageState(page)
- waitUntil: 'domcontentloaded'
- Prefer id= selectors; fall back to text= or role selectors
- Wrap risky steps in .catch(() => {}) or isVisible() checks to avoid flaky failures
- Use test.skip() when data is missing (no rows) rather than hard failing

## File updates
6. Write tests/<feature-name>.spec.ts
7. Update suite-map.json: add to "full" suite + add pattern entry
8. Set E2E_BASE_URL=https://app.connect-x.tech in .env
9. Stage and commit:
   - If `.git/index.lock` exists, remove it first: `rm -f .git/index.lock`
   - `git add tests/<feature>.spec.ts suite-map.json`
   - `git commit -m "test: add <FeatureName> spec (<N> TCs, full CRUD)"`
   - `git push origin <current-branch>`
10. Report: feature chosen, number of TCs written, what CRUD actions were covered, commit hash, push status