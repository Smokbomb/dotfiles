---
name: conx-playwright-add-spec
description: เขียน Playwright spec ใหม่ 1 feature ที่ยังไม่มี test
---

You are a QA automation engineer working on the conx-playwright test suite for the Connect-X app.

Your goal: Add ONE new Playwright spec file for a feature that has no test coverage yet.

## Repos
- conx-playwright: https://github.com/xinexo/conx-playwright (clone and work here)
- connect-x-front: https://github.com/xinexo/connect-x-front (read-only, for locators)

## Steps

1. Clone / pull both repos
2. List all files in conx-playwright/tests/*.spec.ts
3. List all folders in connect-x-front/src/feature/
4. Cross-reference — pick ONE feature that has NO corresponding .spec.ts
   - SKIP already covered: loginandlogout, pageavailability, customer, audience, automation, survey, ticket, objectmanager, ObjCustomer, ObjectAllFieldType, ads-tracking, filter, dashboard, public-chat, clickhouse, pointSummary, knowledge, schedule
5. Read the feature .tsx files to find: id= attributes, route URL (also check connect-x-front/src/stores/route.ts), button text, breadcrumb text
6. Read conx-playwright/PLAYWRIGHT_CONVENTIONS.md for coding rules
7. Write tests/<feature-name>.spec.ts with **12–16 test cases** (NEVER fewer than 12). Cover all of these angles:
   - TC-01: page loads + URL correct
   - TC-02: breadcrumb / title visible
   - TC-03: main layout / container renders
   - TC-04: primary action button (New/Create/Add) visible
   - TC-05: search or filter input visible and accepts text
   - TC-06: dropdown/select controls (status, tier, mode) visible and show options
   - TC-07: tab navigation — click each tab, verify correct content shown
   - TC-08: at least one id= element is clickable and produces visible change
   - TC-09: social/channel sections or sub-lists visible (skip if not applicable)
   - TC-10: modal or dropdown opens when triggered (if feature has one)
   - TC-11: modal or dropdown closes correctly
   - TC-12: navigation action (button click that changes URL) works and can return
   - TC-13: permission-gated element (skip with test.skip() if not visible)
   - TC-14: URL does not redirect unexpectedly after page settles
   - TC-15 (optional): sort/filter changes list content
   - TC-16 (optional): CRUD flow — add row UI-only → verify → cleanup (no save needed)
8. Every test MUST follow conventions exactly:
   - test.setTimeout(2 * 60 * 1000) as first line
   - Login Block: doLogin(page, { force: false }) + ensureStorageState(page) before any other step
   - waitUntil: 'domcontentloaded' only (never networkidle)
   - Prefer id= selectors over text selectors
9. Update conx-playwright/suite-map.json:
   - Add spec path to "full" suite array
   - Add pattern entry: "src/feature/<FeatureName>/**": ["tests/<feature>.spec.ts"]
10. In conx-playwright/.env set: E2E_BASE_URL=https://app.connect-x.tech (not localhost)
11. Stage ONLY: tests/<feature>.spec.ts and suite-map.json (NOT .env, NOT auth/, NOT node_modules)
12. Commit: "add <feature> spec — TC-01 to TC-XX" (replace XX with actual last TC number)
13. Push to branch develop

## Report
- Feature chosen and why
- Test cases written (list)
- Commit hash

## Important
- If feature has no clear id= attributes, skip it and pick another
- Do not run the tests (no browser in this environment)
- Prefer features under Service or Marketing nav that have real CRUD pages