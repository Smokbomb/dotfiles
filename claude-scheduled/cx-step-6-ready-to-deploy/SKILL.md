---
name: cx-step-6-ready-to-deploy
description: [CX Step 6/6] Verify deploy readiness และเตรียม smoke test
---

คุณกำลังช่วยฉันในขั้นตอนที่ 6 ของ Connect-X Development Workflow: **Ready to Deploy**

ดูเอกสาร workflow ฉบับเต็มที่ C:\Users\USER\Documents\GitHub\CONNECT_X_DEV_WORKFLOW.md

ขั้นตอนการทำงาน:
1. ถามฉันว่า task ID และ repo + PR merged แล้วหรือยัง
2. ตรวจสถานะ:
   ```bash
   git checkout production
   git pull
   git log --oneline -5
   ```
   confirm ว่า commit จาก PR อยู่ใน production แล้ว
3. ตรวจ environment ที่ deploy:
   - connect-x-short-link → branch `production-auto-deploy` (auto deploy)
   - repo อื่น → DevOps promote image manually
4. สร้าง smoke test checklist เฉพาะงานนี้:
   - List acceptance criteria จาก task summary
   - URL / endpoint ที่ต้องทดสอบ
   - ขั้นตอนการ verify บน prod
5. ถ้าเป็น breaking change หรือต้อง config ใหม่ — แจ้งเตือน DevOps:
   - ENV variables ที่ต้องเพิ่ม
   - Migration ที่ต้องรัน
   - Feature flag ที่ต้องเปิด
6. Rollback plan:
   - Critical issue → Rollback image ผ่าน GKE
   - Non-critical → เปิด hotfix branch จาก production
7. หลัง deploy + smoke test ผ่าน:
   - บันทึกสถานะ deploy ลง C:\Users\USER\Documents\GitHub\.cx-tasks\CX-XXXX-deployed.md (commit hash, เวลา, env)
   - แจ้งเตือนให้ฉัน close task ใน Notion
8. ถ้า smoke test ไม่ผ่าน — guide ให้ rollback หรือเปิด hotfix branch ทันที