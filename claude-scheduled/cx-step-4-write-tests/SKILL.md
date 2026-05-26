---
name: cx-step-4-write-tests
description: [CX Step 4/6] เขียน automation tests สำหรับ code ที่เพิ่งทำ
---

คุณกำลังช่วยฉันในขั้นตอนที่ 4 ของ Connect-X Development Workflow: **เขียน Automation Test**

ดูเอกสาร workflow ฉบับเต็มที่ C:\Users\USER\Documents\GitHub\CONNECT_X_DEV_WORKFLOW.md

ขั้นตอนการทำงาน:
1. ถามฉันว่า task ID อะไร และ repo ไหน
2. ดูไฟล์ที่เพิ่งแก้: `git diff --name-only production`
3. สำหรับแต่ละไฟล์ที่แก้:
   - Backend service: เขียน unit test `*.spec.ts` ข้างๆ
   - Backend controller / module: เขียน e2e test ใน `test/`
   - Frontend component: เขียน test ใน `__tests__` (Jest + Testing Library)
   - Frontend page / flow: พิจารณา E2E test
4. Test ต้องครอบคลุม:
   - Happy path ตาม acceptance criteria
   - Edge cases (null, empty, unauthorized)
   - **Multi-tenant isolation** — orgId เปลี่ยนแล้วข้อมูลไม่ leak (สำคัญมากสำหรับ Connect-X)
   - Error handling ของ Firestore / RabbitMQ / Redis
5. รัน test:
   - Backend: `npm run test` หรือ `npm run test:cov`
   - Frontend: `yarn test`
6. ถ้า test ไม่ผ่าน — fix code หรือ test แล้วรันใหม่
7. ก่อน commit ให้รันทั้งหมดอีกครั้ง:
   ```bash
   # Backend
   npm run lint && npm run typecheck && npm run test
   # Frontend
   yarn lint && yarn type-check && yarn test
   ```
8. Commit code + test รวมกัน:
   ```bash
   git add .
   git commit -m "CX-XXXX &lt;description&gt;"
   ```
9. รายงาน coverage และ test ที่เพิ่มไป