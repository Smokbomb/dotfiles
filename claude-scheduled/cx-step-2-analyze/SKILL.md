---
name: cx-step-2-analyze
description: [CX Step 2/6] วิเคราะห์ codebase และวางแผน implementation
---

คุณกำลังช่วยฉันในขั้นตอนที่ 2 ของ Connect-X Development Workflow: **วิเคราะห์ (Analyze)**

ดูเอกสาร workflow ฉบับเต็มที่ C:\Users\USER\Documents\GitHub\CONNECT_X_DEV_WORKFLOW.md

ขั้นตอนการทำงาน:
1. ถามฉันว่า task ID อะไร และ repo ไหน (เช่น connect-x, connect-x-front)
2. ถ้ามีไฟล์สรุปจากขั้นตอน 1 (C:\Users\USER\Documents\GitHub\.cx-tasks\CX-XXXX-summary.md) ให้อ่านก่อน
3. อ่าน CLAUDE.md / AGENTS.md ของ repo นั้น
4. ถ้าเป็น backend (connect-x):
   - อ่าน docs/repository-index.md เพื่อหา module ที่เกี่ยว
   - ระบุ service.ts ที่ต้องแก้
   - ตรวจ Critical Invariants:
     * Firestore เป็น source of truth
     * orgId จาก JWT เท่านั้น
     * ใช้ PostgresService.encryptTable()
     * Workers ไม่มี DI — ใช้ publicFunction
     * cx_ prefix สำหรับ system field
5. ถ้าเป็น frontend (connect-x-front):
   - ดู src/pages และ src/components ที่เกี่ยว
   - ตรวจ existing patterns (Tailwind, hooks, i18n via extractedTranslations)
6. วาง implementation plan:
   - ไฟล์ที่ต้องสร้าง/แก้ (พร้อม path)
   - ลำดับการทำ
   - จุดเสี่ยง / edge cases
   - Test strategy
7. บันทึก plan ลง C:\Users\USER\Documents\GitHub\.cx-tasks\CX-XXXX-plan.md

อย่าเพิ่งแก้ code — ขั้นนี้แค่วางแผนเท่านั้น