---
name: cx-step-5-open-pr
description: [CX Step 5/6] Push branch และเตรียมเปิด PR พร้อม description
---

คุณกำลังช่วยฉันในขั้นตอนที่ 5 ของ Connect-X Development Workflow: **เปิด PR**

ดูเอกสาร workflow ฉบับเต็มที่ C:\Users\USER\Documents\GitHub\CONNECT_X_DEV_WORKFLOW.md

ขั้นตอนการทำงาน:
1. ถามฉันว่า task ID และ repo
2. ตรวจ status:
   ```bash
   git status
   git log --oneline production..HEAD
   git diff production --stat
   ```
3. รัน final check:
   - Backend: `npm run lint && npm run typecheck && npm run test`
   - Frontend: `yarn lint && yarn type-check && yarn test`
4. ถ้ายังไม่ push: `git push origin &lt;branch-name&gt;`
5. สร้าง PR description ตาม template:
   ```markdown
   ## Task
   - Notion: [CX-XXXX](link)

   ## What changed
   - (สรุปจาก git diff)

   ## Why
   - (จาก acceptance criteria)

   ## How to test
   1. ...

   ## Screenshots / Recording
   (ถ้าเป็น UI)

   ## Checklist
   - [x] Lint ผ่าน
   - [x] Typecheck ผ่าน
   - [x] Test ผ่าน
   - [ ] อัปเดต docs ถ้าจำเป็น
   - [ ] ทดสอบบน beta/stable
   ```
6. บันทึก PR description ลง C:\Users\USER\Documents\GitHub\.cx-tasks\CX-XXXX-pr.md เพื่อให้ฉัน copy ไป paste บน GitHub
7. แจ้ง URL ที่ฉันต้องไปเปิด PR: `https://github.com/xinexo/&lt;repo&gt;/compare/production...&lt;branch&gt;`
8. แนะนำ reviewers และ labels (ถ้ารู้)