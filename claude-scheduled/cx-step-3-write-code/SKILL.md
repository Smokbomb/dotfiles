---
name: cx-step-3-write-code
description: [CX Step 3/6] เขียน code ตาม plan ที่วางไว้
---

คุณกำลังช่วยฉันในขั้นตอนที่ 3 ของ Connect-X Development Workflow: **เขียน Code**

ดูเอกสาร workflow ฉบับเต็มที่ C:\Users\USER\Documents\GitHub\CONNECT_X_DEV_WORKFLOW.md

ขั้นตอนการทำงาน:
1. ถามฉันว่า task ID อะไร และ repo ไหน
2. อ่าน plan จาก C:\Users\USER\Documents\GitHub\.cx-tasks\CX-XXXX-plan.md (ถ้ามี)
3. ตรวจสอบว่าอยู่ branch ที่ถูกต้อง:
   ```bash
   cd /sessions/.../mnt/GitHub/&lt;repo&gt;
   git branch --show-current
   git status
   ```
   ถ้ายังอยู่ production ให้ checkout branch ใหม่: `git checkout -b CX-XXXX-description`
4. เขียน code ตาม plan ทีละไฟล์ — ทำตาม pattern เดิมของ codebase
5. หลังเขียนเสร็จแต่ละไฟล์/module ใหญ่:
   - Backend: `npm run lint` และ `npm run typecheck`
   - Frontend: `yarn lint` และ `yarn type-check`
6. ถ้าเพิ่ม/ลบ module ใน backend: รัน `npm run docs:generate-module-list`
7. รายงานสิ่งที่แก้: list ของไฟล์ + summary การเปลี่ยนแปลง
8. **ยังไม่ commit** — ให้ฉันดูก่อน (จะ commit ในขั้นถัดไปพร้อม test)

ถ้าเจอ Critical Invariants ของ Connect-X ให้เตือนทันที (เช่น เผลออ่าน orgId จาก body, ใช้ TypeORM, ไม่ใช้ encryptTable)