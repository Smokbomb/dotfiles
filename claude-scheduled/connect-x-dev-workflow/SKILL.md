---
name: connect-x-dev-workflow
description: รัน Connect-X Development Workflow: เช็ค Notion tasks, สรุปสถานะ PR, และแนะนำ next steps ตาม workflow มาตรฐาน
---

## Connect-X Development Workflow Runner

คุณคือ AI assistant ที่ช่วย developer ทำงานตาม Connect-X Development Workflow มาตรฐาน

### Objective
ทบทวนสถานะงานปัจจุบัน และแนะนำ next steps ตาม workflow ด้านล่างนี้

---

### Workflow Overview (Notion → Code → Test → PR → Deploy)

**ขั้นตอนที่ 1 — อ่าน Notion Task**
ใช้ `notion-query-database-view` กับ view ที่ filter `Build from AI = true` ไว้แล้ว:



```

view_url: view://36094d61-b58b-8187-bcfc-000c5f75af8b

```



> View นี้ชื่อ "🤖 AI Analysis Queue" — filter เฉพาะ `Build from AI = __YES__` จาก ConnectX Sprint database ทั้งหมด ไม่ต้องสแกนทุก task

- ตรวจสอบ: Task ID (เช่น CX-XXXX), Acceptance Criteria, scope (backend/frontend/ทั้งคู่)

**ขั้นตอนที่ 2 — วิเคราะห์ (Analyze)**
- อ่าน CLAUDE.md / AGENTS.md ของ repo ที่จะแก้
- Backend checklist:
  - Firestore = source of truth (เขียน Firestore ก่อนเสมอ)
  - Postgres = async mirror (อย่าอ่านข้อมูลที่เพิ่งเขียน)
  - ไม่ใช้ TypeORM — ใช้ `PostgresService.rawQuery(organizeId, sql, params)`
  - `organizeId` จาก JWT (`req.user.organize_id`) เท่านั้น
  - Workers ไม่มี NestJS DI — ใช้ `publicFunction/*.js`
  - ตั้งชื่อ table ผ่าน `PostgresService.encryptTable()`
- Frontend checklist:
  - Vite + React + TypeScript (Node 22.x)
  - Tailwind utility-first
  - ใช้ `yarn gen` สำหรับ scaffold component ใหม่
  - ใช้ `extractedTranslations` สำหรับ i18n

* หา link Figma และต่อด้วยใช้ Figma MCP ที่เชื่อมต่ออยู่

**ขั้นตอนที่ 3 — เขียน Code**
- Branch naming: `CX-XXXX` / `hotfix/CX-XXXX` / `refactor/CX-XXXX`
- Commit message: `CX-XXXX <description>` หรือ `hotfix: <description>`
- ก่อน commit: `npm run lint && npm run typecheck`

**ขั้นตอนที่ 4 — เขียน Automation Test**
- Backend: Jest unit (`*.spec.ts`) + e2e (`test/*.e2e-spec.ts`)
- Frontend: Jest + Testing Library (`__tests__`)
- ครอบคลุม: happy path, edge cases, multi-tenant isolation (orgId), external service errors
- ก่อน push:
  ```bash
  # Backend
  npm run lint && npm run typecheck && npm run test
  # (ถ้าเพิ่ม/ลบ module) npm run docs:generate-module-list

  # Frontend
  yarn lint && yarn type-check && yarn test
  ```

**ขั้นตอนที่ 5 — เปิด PR**
- PR title: `CX-XXXX`
- PR description template ต้องมี: Task link, What changed, Why, How to test, Screenshots (ถ้า UI), Checklist
- Assign reviewers + add labels
- รอ CI: lint, test, build ผ่านก่อน Request Review

* comment Notion ว่า PR แล้ว

**ขั้นตอนที่ 6 — Deploy**
- Merge to production → CI/CD → Cloud Build → Docker image → Artifact Registry → GKE
- Short-link: auto-deploy; repo อื่น: รอ DevOps promote
- Smoke test บน prod → Close task ใน Notion

---

### สิ่งที่ต้องทำเมื่อ task นี้รัน

**Local repos อยู่ที่:** `C:\Users\USER\Documents\GitHub`  
**Repos หลัก:** `connect-x`, `connect-x-front`, `connect-x-mpi`, `connect-x-portal`, `connect-x-short-link`

1. **Notion MCP:** ค้นหา tasks ที่มีสถานะ `Build from AI = YES` และ title/tag มีคำว่า "CX-" แล้วแสดงสรุป  
   **ข้ามทันที** ถ้า task มี status เป็น `Wait Test Production`, `Done`, หรือ `Production` — ไม่ต้องหยิบมาทำงาน
2. **Local Git (แทน GitHub MCP):** ใช้คำสั่ง `git -C <repo-path> branch` และ `git -C <repo-path> log --oneline -10` เพื่อเช็ค branches และ commits ล่าสุดของแต่ละ repo — หา branches ที่ขึ้นต้นด้วย `CX-` เพื่อดูงานที่กำลัง active
3. **Figma MCP:** ถ้า task มี Figma link ให้ดึง design context มาประกอบการวิเคราะห์
4. **สรุป next steps** ที่ชัดเจนตาม workflow ด้านบน โดยอ้างอิงจากสถานะที่พบ
5. **Highlight ถ้ามี:** tasks ที่ค้างนาน, branches ที่ยังไม่ merge, หรือ lint/typecheck ที่ fail

แสดงผลลัพธ์เป็นภาษาไทย ในรูปแบบที่อ่านง่าย พร้อม action items ที่ชัดเจน