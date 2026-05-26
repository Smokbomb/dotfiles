---
name: notion-rd-paiboon-analysis
description: วิเคราะห์ Notion tasks Use AI = Yes หรือ true เท่านั้น และ comment solution อัตโนมัติทุก 3 ชั่วโมง
---

## Notion R&D Task Workflow — Auto Run สำหรับ Paiboon Toomthong

รัน workflow วิเคราะห์ Notion tasks และ comment solution อัตโนมัติ

---

### ขั้นตอน

**Step 1 — ค้นหา Tasks ของ Notion**

ใช้ `notion-query-database-view` กับ view ที่ filter `Use AI = true` ไว้แล้ว:

```
view_url: view://36094d61-b58b-8187-bcfc-000c5f75af8b
```

> View นี้ชื่อ "🤖 AI Analysis Queue" — filter เฉพาะ `Use AI = __YES__` จาก ConnectX Sprint database ทั้งหมด ไม่ต้องสแกนทุก task

ผลลัพธ์ที่ได้คือ JSON `results[]` — แต่ละ item มี fields สำคัญ:
- `Task ID` — ตัวเลข เช่น `"3612"` (ใช้เป็น `CX-3612`)
- `url` — Notion page URL เช่น `https://www.notion.so/36094d61...`
- `Task name` — ชื่อ task
- `Status` — สถานะปัจจุบัน
- `Issue Type ` — ประเภท (Bug / Task / Story ฯลฯ) **หมายเหตุ: มีช่องว่างหลัง "Type"**
- `Use AI` — จะเป็น `"__YES__"` เสมอ (view filter การันตีแล้ว)

**หลังได้ results — skip tasks ที่ Status เป็น:**
- `Production`
- `Done`
- `Wait Test Production`

tasks ที่เหลือดำเนินการต่อ Step 2-4 ทันที

---

**Step 2 — เช็คว่าเคย Comment ไปแล้วหรือยัง**

สำหรับแต่ละ task ที่เหลือ ใช้ `notion-get-comments` ดึง comments ของ page นั้น (ใช้ UUID จาก `url` field)

- ถ้ามี comment ที่มีข้อความ "จากเพื่อน" หรือ "🤖 Analysis จากเพื่อน" อยู่แล้ว → ข้ามทันที
- ถ้ายังไม่มี → ทำ Step 3-4

---

**Step 3 — อ่านเนื้อหา Task และวิเคราะห์**

ใช้ `notion-fetch` อ่านเนื้อหาเต็มของ page (ใช้ `url` จาก Step 1)

สังเกต field สำคัญ:
- **Issue Type** — "Task" หรือ "Bug"
- **Description / BUG fields** — อาการ, root cause, expected result

**ถ้า Issue Type = Task:**
เปิด code repo ที่ `C:\Users\USER\Documents\GitHub\` วิเคราะห์:
- Backend: `connect-x/src/modules/` (NestJS + TypeScript)
- Frontend: `connect-x-front/src/feature/` (React 17 + Recoil)
ใช้ Grep หา files ที่เกี่ยวข้อง, Read อ่าน service/interface/entity ที่สำคัญ
สังเกต code ที่ comment out ไว้ — มักเป็น feature ที่รอ implement

**ถ้า Issue Type = Bug:**
วิเคราะห์อาการจาก task description แล้วหา root cause เบื้องต้นจาก codebase
จากนั้น:
1. หา solution เหมือน type อื่นๆ
2. ใส่เฉพาะ Root Cause (Internal) และ Fix steps ใน comment เท่านั้น ไม่ต้องใส่ Customer Reply ใน comment

---

**Step 4 — อัปเดต Field และ Comment ใน Notion**

**สำหรับ Bug tasks — อัปเดต field ก่อน:**
ใช้ `notion-update-page` เขียน Customer Reply ลง field `Bug: Root Cause for Customer`:
- ข้อความต้องเป็นภาษากลางๆ ไม่เปิดเผยข้อมูลภายใน (ดูกฎด้านล่าง)

**จากนั้น comment สำหรับทุก task ที่ยังไม่มี comment:**
ใช้ `notion-create-comment` โพสต์ลงทุก page

**โครงสร้าง comment สำหรับ Issue Type = Task:**

```
🤖 Analysis จากเพื่อน
━━━━━━━━━━━━━━━━━━━━━━
📋 CX-XXXX: ชื่องาน
━━━━━━━━━━━━━━━━━━━━━━

🔍 สิ่งที่พบจาก codebase:
[file ที่เกี่ยวข้อง, สถานะปัจจุบัน, สิ่งที่ยังขาด]

✅ แนวทาง Solution:
Step 1 [Frontend] – ...  @Jirayu
Step 2 [Backend] – ...   @Tanapat

🧪 Test Cases:  @Now
1. Happy path: ...
2. Edge case: ...
3. Error case: ...

⚠️ หมายเหตุ: ...
```

**โครงสร้าง comment สำหรับ Issue Type = Bug:**

```
🤖 Analysis จากเพื่อน
━━━━━━━━━━━━━━━━━━━━━━
🐛 CX-XXXX: ชื่อ bug
━━━━━━━━━━━━━━━━━━━━━━

🔍 Root Cause (Internal):
[สาเหตุจริงๆ ที่พบจาก code/log — เป็นข้อมูลภายในเท่านั้น]

✅ แนวทาง Fix:
Step 1 [Frontend] – ...  @Jirayu
Step 2 [Backend] – ...   @Tanapat

🧪 Test Cases:  @Now
1. Happy path: ...
2. Edge case: ...
3. Error case: ...

⚠️ หมายเหตุ: ...
```

**กฎการ mention ใน comment (สำคัญมาก):**
- Tag lead **ตรงใน step ที่เกี่ยวข้องเลย** ไม่ต้องรวมไว้ที่ cc บรรทัดท้าย
- Step ที่เป็น Frontend → mention @Jirayu ตรงนั้น
- Step ที่เป็น Backend → mention @Tanapat ตรงนั้น
- หัว Test Cases → mention @Now ตรงนั้น (ทั้ง Task และ Bug ต้องมีเสมอ)
- ถ้า task มีทั้ง Frontend และ Backend → mention ทั้ง @Jirayu และ @Tanapat แต่ละ step ของตัวเอง

**⚠️ วิธี mention ที่ถูกต้อง — ใช้ `rich_text` parameter เท่านั้น (ห้ามใช้ markdown):**

`notion-create-comment` ต้องส่ง `rich_text` array เสมอเมื่อมี mention — ห้ามใช้ `markdown` parameter เพราะ `<mention-user url="..."/>` ใน markdown ไม่ render ใน Notion

รูปแบบ rich_text สำหรับ mention:
```json
[
  {"type": "text", "text": {"content": "ข้อความก่อน mention "}},
  {"type": "mention", "mention": {"type": "user", "user": {"object": "user", "id": "USER_ID_HERE"}}},
  {"type": "text", "text": {"content": "\nข้อความต่อไป"}}
]
```

ตัวอย่าง comment ที่มีทั้ง Backend + Test Cases:
```json
[
  {"type": "text", "text": {"content": "Step 1 [Backend] — แก้ไข service.ts "}},
  {"type": "mention", "mention": {"type": "user", "user": {"object": "user", "id": "20ad872b-594c-81ef-8817-00024419dba8"}}},
  {"type": "text", "text": {"content": "\n\n🧪 Test Cases: "}},
  {"type": "mention", "mention": {"type": "user", "user": {"object": "user", "id": "20ad872b-594c-8135-8f93-0002d3b6caac"}}},
  {"type": "text", "text": {"content": "\n1. Happy path: ...\n2. Edge case: ..."}}
]
```

**ข้อจำกัด**: rich_text array รวมกันต้องไม่เกิน 2,000 ตัวอักษรต่อ content block — แบ่ง comment หลาย block ถ้าจำเป็น

---

### กฎ Customer Reply (Bug — เขียนลง field `Bug: Root Cause for Customer` เท่านั้น)

ข้อความต้อง **ไม่เปิดเผยข้อมูลภายใน** เช่น config ผิด, server down, code bug, database error ฯลฯ
ให้ใช้ภาษากลางๆ ที่ฟังดูเป็นมิตรและไม่ทำให้ลูกค้าตื่นตระหนก

| Root Cause จริง | ตอบลูกค้าว่า |
|---|---|
| Server down / crash | "ขณะนี้ระบบมีปริมาณการใช้งานสูงกว่าปกติ ทีมงานกำลังดำเนินการแก้ไขอยู่ค่ะ" |
| Config ผิด / misconfiguration | "ระบบอยู่ระหว่างการปรับปรุงค่าตั้งค่า ขออภัยในความไม่สะดวกค่ะ" |
| Database error / timeout | "ระบบมีปริมาณ traffic สูง ทำให้การดึงข้อมูลล่าช้า กำลังเร่งแก้ไขค่ะ" |
| Third-party API ล้มเหลว | "ระบบที่เชื่อมต่ออยู่มีความล่าช้าชั่วคราว ทีมงานกำลังติดตามอยู่ค่ะ" |
| Bug ใน code | "พบปัญหาการทำงานที่ไม่คาดคิด ทีมงานกำลังเร่งตรวจสอบและแก้ไขค่ะ" |
| Permission / auth error | "พบปัญหาการเข้าถึงระบบชั่วคราว กรุณาลองใหม่อีกครั้งหรือติดต่อทีมงานค่ะ" |

หลักการ: ตอบแบบ "เรากำลังดูแลอยู่" โดยไม่ระบุว่าเกิดจากอะไรภายใน

---

### กฎการ Mention Lead (CX task เท่านั้น)

| ประเภทงาน | @mention | Notion User ID |
|-----------|----------|----------------|
| Backend | @Tanapat Mangsakul | `20ad872b-594c-81ef-8817-00024419dba8` |
| Frontend / Flutter | @Jirayu Engkasuwansiri | `20ad872b-594c-8108-9185-0002c4894222` |
| QA / Test Cases | @Now Seemoungkum | `20ad872b-594c-8135-8f93-0002d3b6caac` |

กฎ mention:
- **Mention ตรง step ที่เกี่ยวข้องในเนื้อ comment เลย** — ไม่ใส่ cc รวมไว้ท้าย comment
- step ที่เป็น Backend → mention @Tanapat ตรงบรรทัดนั้นทันที
- step ที่เป็น Frontend/Flutter → mention @Jirayu ตรงบรรทัดนั้นทันที
- หัวข้อ Test Cases → mention @Now ตรงนั้นเสมอ (ทั้ง Task และ Bug)
- task ที่มีทั้ง Frontend และ Backend → mention แต่ละ lead ตรง step ของตัวเอง ไม่รวมกัน
- DEV task (ไม่มีทั้ง Frontend/Backend/Test) → comment เฉยๆ ไม่ต้อง mention ใคร

---

### Step 5 — เรียนรู้และอัปเดต SKILL.md หลังรัน

หลังจาก comment ครบทุก task แล้ว ให้ทบทวนว่ามีอะไรที่เรียนรู้เพิ่มเติมจากการรันครั้งนี้หรือไม่ เช่น:
- format หรือ tool ที่ใช้ไม่ถูกต้อง → แก้ไขใน SKILL.md
- user ID ที่ผิด → อัปเดตตาราง lead
- กฎใหม่ที่ควรจำ → เพิ่มใน SKILL.md
- ปัญหาที่เจอและวิธีแก้ → บันทึกไว้ใน section "Lessons Learned"

ใช้ `mcp__scheduled-tasks__update_scheduled_task` กับ taskId `notion-rd-paiboon-analysis` เพื่ออัปเดต prompt ได้เลย

---

### สรุปผลหลังรัน

แจ้งให้รู้ว่า:
- Task ที่ comment ใหม่ไปกี่ task (พร้อมชื่อ)
- Task ที่ข้ามเพราะมี comment แล้วกี่ task
- Task ที่ข้ามเพราะ Status = Done/Production/Wait Test Production กี่ task
- สิ่งที่เรียนรู้และอัปเดต SKILL.md ในครั้งนี้ (ถ้ามี)