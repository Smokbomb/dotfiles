---
name: notion-solution
description: รัน workflow วิเคราะห์ Notion tasks และ comment solution อัตโนมัติ
---

รัน workflow วิเคราะห์ Notion tasks และ comment solution อัตโนมัติ



---



### Config



```

LINE_GROUP_DEV = Cf53cc4458d4ad0b33e9c54d5e630c2a3      # Task / Story / Feature ทั่วไป
LINE_GROUP_BUG = Cff593dd16c465d61ee5c0a3e9776dcf1      # Issue Type = Bug หรือ Inquiry

```



(CHANNEL_ACCESS_TOKEN อยู่ใน LINE Bot MCP config แล้ว ไม่ต้องเก็บ inline)



**กฎ routing:**

- `Issue Type ` เป็น `Bug` หรือ `Inquiry` → ส่งไปที่ `LINE_GROUP_BUG` (`Cff593dd16c465d61ee5c0a3e9776dcf1`)

- Issue Type อื่นๆ ทั้งหมด (Task, Story, ฯลฯ) → ส่งไปที่ `LINE_GROUP_DEV` (`Cf53cc4458d4ad0b33e9c54d5e630c2a3`)



---



### LINE Notification Helper



**วิธีส่ง LINE notification ทุกครั้ง:** ใช้ `mcp__line-bot__push_text_message` โดยตรง

เลือก `userId` ตาม Issue Type ของ task:

- `Issue Type ` = `Bug` หรือ `Inquiry` → `userId: Cff593dd16c465d61ee5c0a3e9776dcf1`

- Issue Type อื่น → `userId: Cf53cc4458d4ad0b33e9c54d5e630c2a3`



**Format ข้อความแจ้งผล:**

- Task วิเคราะห์เสร็จ: `✅ [CX-XXXX] ชื่อ task\nวิเคราะห์เสร็จแล้ว — comment solution + Story Points ลง Notion แล้วครับ`

- Requirement ไม่ครบ: `⚠️ [CX-XXXX] ชื่อ task\nRequirement ยังไม่ครบ (~XX%) — tag SD/Reporter แล้ว รอข้อมูลเพิ่มเติมครับ`

- Needs Info วิเคราะห์ซ้ำเสร็จ: `✅ [CX-XXXX] ชื่อ task\nมี req ใหม่จาก SD/PO — วิเคราะห์ซ้ำเสร็จแล้ว comment ลง Notion แล้วครับ`

- Needs Info ยังรอ: (ไม่ต้องยิง LINE — ข้ามเงียบๆ)



---



### ขั้นตอน



**Step 1 — ค้นหา Tasks ของ Notion**



**Pre-flight: ตรวจสอบ Property "AI Analyzed" (ทำครั้งเดียว)**

ตรวจสอบว่า ConnectX Sprint database มี property ชื่อ `AI Analyzed` (type: **Select** มี 2 ตัวเลือก: `Done` และ `Needs Info`) หรือไม่

- ถ้ายังไม่มี → แจ้ง user ให้เพิ่ม Select property ชื่อ `AI Analyzed` (options: "Done", "Needs Info") ใน Notion database ก่อน แล้วค่อยรันต่อ (Notion view "🤖 AI Analysis Queue" ควรมี filter `AI Analyzed is not "Done"` ด้วยเพื่อให้ทั้ง null และ "Needs Info" เข้า queue)

- ถ้ามีแล้ว → ดำเนินการต่อ



**โหลด Fallback Local File:**

อ่านไฟล์ `C:\Users\USER\Documents\GitHub\.claude\scheduled\notion-rd-paiboon-analysis\processed_tasks.json`

- ถ้าไฟล์ไม่มี → ถือว่า `processed_tasks = {}`

- ถ้ามี → parse JSON เป็น object `processed_tasks` (key = Task ID, value = `{ status, last_comment_at }`)



Format ของ `processed_tasks.json`:

```json

{

  "3612": { "status": "Done", "last_comment_at": "2026-05-26T11:00:00.000Z" },

  "3450": { "status": "Needs Info", "last_comment_at": "2026-05-26T09:30:00.000Z" }

}

```



ใช้ `notion-query-database-view` กับ view ที่ filter `Use AI = true` ไว้แล้ว:



```

view_url: view://36094d61-b58b-8187-bcfc-000c5f75af8b

```



> View นี้ชื่อ "🤖 AI Analysis Queue" — filter เฉพาะ `Use AI = __YES__` และ `AI Analyzed is not "Done"` จาก ConnectX Sprint database ดังนั้น results จะมีได้ 2 แบบ: task ใหม่ (AI Analyzed = null) และ task ที่รอข้อมูลเพิ่ม (AI Analyzed = "Needs Info")



ผลลัพธ์ที่ได้คือ JSON `results[]` — แต่ละ item ดึงเฉพาะ fields ที่จำเป็น:

- `Task ID` — ตัวเลข เช่น `"3612"` (ใช้เป็น `CX-3612`)

- `url` — Notion page URL เช่น `https://www.notion.so/36094d61...`

- `Task name` — ชื่อ task

- `Status` — สถานะปัจจุบัน

- `Issue Type ` — ประเภท (Bug / Task / Story ฯลฯ) **หมายเหตุ: มีช่องว่างหลัง "Type"**

- `AI Analyzed` — Select property ("Done" / "Needs Info" / null)

- `SD` — Solution Designer / owner ของ task

- `Reporter` — ผู้รายงาน

- `last_edited_time` — เวลาที่ page ถูกแก้ไขล่าสุด (ISO 8601) — ใช้สำหรับ Step 1.5



> `Use AI` ไม่ต้องดึงแล้ว — view filter การันตีว่าเป็น `__YES__` เสมอ



**หลังได้ results — skip tasks ที่:**

- Status เป็น `Production`, `Done`, หรือ `Wait Test Production`

- `AI Analyzed = "Done"` — property บอกว่า AI จัดการแล้ว (view filter ควร filter ออกแล้ว แต่เป็น safety net)

- Task ID อยู่ใน `processed_tasks` และ `status = "Done"` — fallback safety net



**แยกประเภท tasks ที่เหลือ:**

- `AI Analyzed = "Needs Info"` → ไปที่ **Step 1.5** (จัดการ Needs Info flow)

- `AI Analyzed = null/empty` (task ใหม่) → ไปที่ **Step 3** ตามปกติ



---



**Step 1.5 — จัดการ Tasks ที่ `AI Analyzed = "Needs Info"`**



> ขั้นตอนนี้ทำเฉพาะ tasks ที่ `AI Analyzed = "Needs Info"` เท่านั้น — tasks ใหม่ข้ามไป Step 3 โดยตรง



สำหรับแต่ละ task ที่ "Needs Info":



**1. เช็ค last_edited_time ก่อนเรียก comments (ประหยัด token):**

- ดึง `last_comment_at` จาก `processed_tasks[task_id]?.last_comment_at`

- เปรียบเทียบกับ `last_edited_time` ของ task ที่ได้จาก query:

  - ถ้า `last_edited_time <= last_comment_at` → **ข้าม task นี้ทันที** (ไม่มีอะไรเปลี่ยนแปลงตั้งแต่ comment ล่าสุด ไม่ต้องเรียก `notion-get-comments` และไม่ต้องยิง LINE)

  - ถ้า `last_edited_time > last_comment_at` (หรือ `last_comment_at` ไม่มี) → ดำเนินการขั้นตอนถัดไป



**2. ดึง comments ของ task:**

ใช้ `notion-get-comments` โดย pass `page_id` เป็น UUID (ไม่ใช่ full URL) — ตัวอย่าง: `35894d61-b58b-8063-9573-e1d14af4695c`



**3. หา timestamp ของ comment ล่าสุดจากเพื่อน:**

- User ID ของเพื่อน: `dbb61c7f-acee-4b92-91ba-892ce248ef29`

- ค้นหา comment ทั้งหมดที่ `created_by.id == "dbb61c7f-acee-4b92-91ba-892ce248ef29"` แล้วเอา `created_time` ล่าสุด → เรียกว่า `last_our_comment_time`

- ถ้าหา comment จากเพื่อนไม่เจอเลย → ถือว่า `last_our_comment_time = null`



**4. ตรวจสอบว่ามี comment ใหม่จาก SD/PO หลัง `last_our_comment_time` ไหม:**

- ดึง `SD` และ `PO` user IDs จาก task properties

- ค้นหา comment ที่ `created_time > last_our_comment_time` และ `created_by.id` อยู่ใน SD หรือ PO IDs

- **ถ้าไม่มี comment ใหม่** → **ข้าม task นี้ทันที** (ไม่ comment ซ้ำ ไม่อัปเดต property ใดๆ ไม่ยิง LINE)



**5. ถ้ามี comment ใหม่จาก SD/PO → วิเคราะห์ requirement ใหม่ทั้งหมด:**

ใช้ `notion-fetch` อ่านเนื้อหา task เต็ม (ไม่แค่ comment) รวมกับเนื้อหาใน comments ใหม่เพื่อประเมิน requirement completeness ใหม่อีกครั้ง



- **ถ้า req ≥ 80%:**

  1. วิเคราะห์ codebase และเขียน solution (ตาม Step 4)

  2. comment solution พร้อม Story Points (ตาม Step 4a + 4b)

  3. set `AI Analyzed = "Done"` (ตาม Step 4c) และบันทึก processed_tasks.json

  4. **ยิง LINE notification** ด้วย `mcp__line-bot__push_text_message` (routing ตาม Issue Type): `✅ [CX-XXXX] ชื่อ task\nมี req ใหม่จาก SD/PO — วิเคราะห์ซ้ำเสร็จแล้ว comment ลง Notion แล้วครับ`



- **ถ้า req < 80%:**

  1. comment แจ้งว่ายังขาดอะไรอยู่ (ตาม format ของ Step 3b)

  2. set `AI Analyzed = "Needs Info"` ไว้เหมือนเดิม (ไม่เพิ่มใน processed_tasks.json เพื่อให้กลับมาใน queue รอบหน้า)

  3. อัปเดต `last_comment_at` ใน processed_tasks.json

  4. **ยิง LINE notification** ด้วย `mcp__line-bot__push_text_message` (routing ตาม Issue Type): `⚠️ [CX-XXXX] ชื่อ task\nยังขาด req อยู่ (~XX%) — tag SD/PO แล้ว รอข้อมูลเพิ่มอีกรอบครับ`



---



**Step 2 — (ยกเลิก) ตรวจสอบ Comments ซ้ำ**



ขั้นตอนนี้ถูกแทนที่ด้วยการ filter ตั้งแต่ Step 1:

1. Notion property `AI Analyzed = "Done"` กรอง task ที่จัดการแล้วออกตั้งแต่ query

2. `processed_tasks.json` เป็น fallback safety net

3. Task ที่ `AI Analyzed = "Needs Info"` จัดการแยกใน Step 1.5



tasks ที่ผ่าน Step 1 (ที่เป็น task ใหม่) ถือว่ายังไม่เคยได้รับ analysis → ดำเนินการ Step 3 ได้เลย ไม่ต้องเรียก `notion-get-comments`



---



**Step 3 — ประเมิน Requirement Completeness**



ก่อน analyze codebase ทุกครั้ง ให้ประเมินว่า requirement พร้อมทำหรือยัง โดยตรวจสอบ:



**สิ่งที่ต้องมีครบก่อน dev ได้:**

- Happy flow ชัดเจนครบทุก step

- Error handling ระบุครบ ไม่มีข้อที่ "ยังไม่แน่ใจ" ค้างอยู่

- Technical dependency ชัด (เช่น API ที่ต้อง integrate, schema ที่ต้องใช้, field ที่ต้อง map)

- Scope ชัด (ใช้ env ไหน, permission ใคร)



**เกณฑ์:**

- **≥ 80%** → ดำเนินการ Step 4 (analyze + comment) ต่อได้เลย

- **< 80%** → **หยุดทันที** อย่า analyze codebase — ให้ทำแค่ Step 3b แล้วข้าม task นี้



---



**Step 3b — ถ้า Requirement < 80% — Comment ขอข้อมูลเพิ่ม**



ใช้ `notion-create-comment` โพสต์ comment แจ้ง SD/Reporter ให้มาเติม requirement



ดึง user ID ของ SD จาก field `SD` ของ task (UUID ใน `user://...`) ถ้าไม่มี SD ให้ใช้ `Reporter` แทน



**โครงสร้าง comment:**



```

⚠️ Requirement ยังไม่ครบ (~XX%) — ขอข้อมูลเพิ่มก่อน dev ได้เลยครับ @SD_หรือ_Reporter



สิ่งที่ยังขาด และเป็น blocker ก่อน dev ได้:



1. [หัวข้อที่ขาด] — [อธิบายว่าขาดอะไรและทำไมถึง block]

2. [หัวข้อที่ขาด] — [อธิบายว่าขาดอะไรและทำไมถึง block]

...

```



**กฎสำหรับ comment นี้:**

- mention SD หรือ Reporter ตรงในประโยคเปิดเลย (rich_text)

- ระบุ % ที่ประเมินไว้

- ระบุ blocker แต่ละข้อให้ชัด บอกว่าขาดอะไรและทำไมถึง block dev ได้

- ห้าม analyze codebase หรือเขียน solution ใดๆ ใน comment นี้

- หลังโพสต์ comment แล้ว → อัปเดต AI Analyzed และบันทึก timestamp แล้วข้ามไป task ถัดไป:

  1. ใช้ `notion-update-page` set `AI Analyzed = "Needs Info"` (Select) บน page นั้น

  2. **บันทึก** `processed_tasks[task_id] = { "status": "Needs Info", "last_comment_at": new Date().toISOString() }` ลง processed_tasks.json

  3. **ยิง LINE notification** ด้วย `mcp__line-bot__push_text_message` (routing ตาม Issue Type): `⚠️ [CX-XXXX] ชื่อ task\nRequirement ยังไม่ครบ (~XX%) — tag SD/Reporter แล้ว รอข้อมูลเพิ่มเติมครับ`

- ไม่ต้องทำ Step 4-4b สำหรับ task นี้



---



**Step 4 — อ่านเนื้อหา Task และวิเคราะห์ (เฉพาะ task ที่ผ่าน ≥ 80%)**



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



**Step 4a — อัปเดต Field และ Comment ใน Notion**



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



**ข้อจำกัด**: rich_text array รวมกันต้องไม่เกิน 2,000 ตัวอักษรต่อ content block — แบ่ง comment หลาย block ถ้าจำเป็น



---



**Step 4b — Reply Story Points ใน thread เดียวกัน**



หลังโพสต์ analysis comment แล้ว ให้ reply ต่อใน thread เดิมทันที (ดึง discussion_id ด้วย `notion-get-comments` อีกครั้ง)



ประเมิน Story Points จากมุมมอง **human dev** ที่คุ้นเคย codebase ระดับ intermediate ไม่ใช่ AI ทำ



**กฎการคำนวน (ใช้เฉพาะภายใน ห้ามแสดงสูตรใน comment):**

- Backend: 1 manday = 2 points

- Frontend: 1 manday = 2 points

- Tester: 1 manday = 8 points



**โครงสร้าง reply points:**



```

📊 ประเมิน Story Points (Human Dev)

━━━━━━━━━━━━━━━━━━━━━━



🔧 Backend — X points  @Tanapat

  Y.Y day — [งานชิ้นที่ 1]

  Y.Y day — [งานชิ้นที่ 2]

  ...



🎨 Frontend — X points  @Jirayu

  Y.Y day — [งานชิ้นที่ 1]

  Y.Y day — [งานชิ้นที่ 2]

  ...



🧪 Tester — X points  @Now

  Y.Y day — [งานชิ้นที่ 1]

  Y.Y day — [งานชิ้นที่ 2]

  ...

```



**กฎสำหรับ reply points:**

- ห้ามแสดงสูตรการคำนวน (เช่น "3.5 manday × 2 = 7 points") ใน comment

- ห้ามมี summary รวม points ท้าย comment

- mention @Tanapat, @Jirayu, @Now ตรงหัวแต่ละ section (ใช้ rich_text)

- ถ้า task เป็น Backend อย่างเดียว ไม่ต้องมี section Frontend (และกลับกัน)

- Tester section ต้องมีเสมอ (ทั้ง Task และ Bug)



---



**Step 4c — อัปเดต AI Analyzed, บันทึก Local, และยิง LINE**



หลัง reply Story Points เรียบร้อยแล้ว — ทำ 3 ขั้นตอนนี้ก่อนไป task ถัดไป:



1. **อัปเดต Notion property:**

   ใช้ `notion-update-page` set `AI Analyzed = "Done"` (Select) บน page นั้น



2. **บันทึก Local Fallback:**

   อ่านไฟล์ `C:\Users\USER\Documents\GitHub\.claude\scheduled\notion-rd-paiboon-analysis\processed_tasks.json`

   - ถ้าไม่มี → สร้างใหม่เป็น `{}` (ต้องสร้าง directory ก่อนด้วย bash: `mkdir -p`)

   - set `processed_tasks[task_id] = { "status": "Done", "last_comment_at": new Date().toISOString() }` → write กลับ

   - ใช้ bash เขียนไฟล์: `cat > "/sessions/.../mnt/GitHub/.claude/scheduled/notion-rd-paiboon-analysis/processed_tasks.json" << 'EOF' ... EOF`

   ```json

   {

     "3612": { "status": "Done", "last_comment_at": "2026-05-26T11:00:00.000Z" }

   }

   ```



3. **ยิง LINE notification** ด้วย `mcp__line-bot__push_text_message` โดย routing ตาม Issue Type:

   - Bug/Inquiry → `userId: Cff593dd16c465d61ee5c0a3e9776dcf1`

   - อื่นๆ → `userId: Cf53cc4458d4ad0b33e9c54d5e630c2a3`

   ```

   ✅ [CX-XXXX] ชื่อ task\nวิเคราะห์เสร็จแล้ว — comment solution + Story Points ลง Notion แล้วครับ

   ```



> **สรุป pattern การ set `AI Analyzed`, บันทึก processed_tasks.json, และยิง LINE:**

> - Step 3b (req < 80% task ใหม่) → set `"Needs Info"` + บันทึก `{ status: "Needs Info", last_comment_at: now }` + **ยิง LINE ⚠️** (routing ตาม Issue Type)

> - Step 1.5 (req < 80% จาก Needs Info) → set `"Needs Info"` + อัปเดต `{ status: "Needs Info", last_comment_at: now }` + **ยิง LINE ⚠️** (routing ตาม Issue Type)

> - Step 1.5 (req ≥ 80% วิเคราะห์ซ้ำสำเร็จ) → เข้า flow Step 4c → set `"Done"` + บันทึก + **ยิง LINE ✅** (routing ตาม Issue Type)

> - Step 4c (analysis ครบ) → set `"Done"` + บันทึก + **ยิง LINE ✅** (routing ตาม Issue Type)

> - กรณีข้าม (ไม่มี comment ใหม่จาก SD/PO) → **ไม่ยิง LINE**



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



### Lessons Learned



**2026-05-26 — Run ครั้งแรก**

- Step 2 เดิมเช็คเฉพาะ "จากเพื่อน" / "🤖 Analysis จากเพื่อน" แต่ comment ประเภท "⚠️ Requirement ยังไม่ครบ" (Step 3b) ไม่มีข้อความนั้น ทำให้รันครั้งถัดไปจะโพสต์ requirement-incomplete comment ซ้ำ

- แก้ไข: เพิ่มกฎใน Step 2 ว่า ถ้ามี comment จาก user-url ของ เพื่อน (`dbb61c7f-acee-4b92-91ba-892ce248ef29`) ใดๆ ก็ตาม → ข้ามทันที



**2026-05-26 — Token Optimization**

- แทน Step 2 (notion-get-comments ทุก task) ด้วย property `AI Analyzed` + `processed_tasks.json`

- ลด fields ที่ query: ตัด `Use AI` ออก (view filter การันตีแล้ว)

- เพิ่ม Step 4c: อัปเดต `AI Analyzed = true` และบันทึก processed_tasks.json หลัง comment ทุกครั้ง (ทั้ง Step 3b และ 4c)



**2026-05-26 — Token Optimization v2 (last_edited_time + last_comment_at)**

- เพิ่ม `last_edited_time` ใน query fields เพื่อนำมาเปรียบเทียบใน Step 1.5

- เปลี่ยน format `processed_tasks.json` จาก `{ "processed": ["id1", "id2"] }` เป็น object keyed by task_id: `{ "3612": { "status": "Done", "last_comment_at": "..." } }`

- Step 1.5: เช็ค `last_edited_time <= last_comment_at` ก่อนเรียก `notion-get-comments` — ถ้าไม่มีการแก้ไข page หลัง comment ล่าสุด → ข้ามได้เลย ประหยัด API call

- Step 3b และ Step 1.5 (Needs Info) ตอนนี้ **บันทึก** `last_comment_at` ลง processed_tasks.json ด้วย (ไม่ใช่แค่ Skip append แล้ว)



**2026-05-26 — Needs Info Loop**

- เปลี่ยน property `AI Analyzed` จาก **Checkbox** เป็น **Select** (`Done` / `Needs Info`) เพื่อให้ task ที่ req < 80% กลับมาใน queue ได้

- view filter เปลี่ยนเป็น `AI Analyzed is not "Done"` — ทำให้ทั้ง null และ "Needs Info" เข้า queue

- เพิ่ม **Step 1.5**: ตรวจ comment ใหม่จาก SD/PO ก่อนวิเคราะห์ซ้ำ — ถ้าไม่มี comment ใหม่ → ข้าม (ไม่ spam comment)

- Step 3b เปลี่ยนจาก `set AI Analyzed = true (checkbox)` → `set AI Analyzed = "Needs Info" (select)` และ**ไม่** append processed_tasks.json

- Step 4c เปลี่ยนจาก `set AI Analyzed = true` → `set AI Analyzed = "Done"` เท่านั้นที่ append processed_tasks.json



**2026-05-26 — เปลี่ยน LINE Notification จาก curl เป็น LINE Bot MCP**

- `curl` ถูก block โดย sandbox proxy (`localhost:3128`) → `403 Forbidden / blocked-by-allowlist`

- ติดตั้ง `@line/line-bot-mcp-server` (npm) ผ่าน `npx` ใน `claude_desktop_config.json`

- เปลี่ยน LINE Notification Helper จาก `mcp__workspace__bash curl` เป็น `mcp__line-bot__push_text_message`

- CHANNEL_ACCESS_TOKEN อยู่ใน MCP config แล้ว ไม่ต้องเก็บ inline ใน prompt

- LINE_GROUP_ID (`C5d8839ddd1af5cb719f3592e7c56290f`) ยังเก็บไว้ใน Config สำหรับ reference ใช้เป็น `userId` parameter ของ tool



**2026-05-27 — แก้ path processed_tasks.json + notion-get-comments UUID**

- `C:\Users\USER\Documents\Claude\Scheduled\...` ไม่ถูก mount ใน bash sandbox → ไม่สามารถอ่าน/เขียนได้

- เปลี่ยน path เป็น `C:\Users\USER\Documents\GitHub\.claude\scheduled\notion-rd-paiboon-analysis\processed_tasks.json` ซึ่งอยู่ใน GitHub folder ที่ถูก mount แล้ว

- ใช้ bash `cat > "...mnt/GitHub/.claude/scheduled/..." << 'EOF'` แทน Write tool (Write tool ถูก block นอก connected folder)

- `notion-get-comments` ต้อง pass `page_id` เป็น UUID มี dash เท่านั้น (**ไม่ใช่** full URL) เช่น `35894d61-b58b-8063-9573-e1d14af4695c`



**2026-05-31 — LINE Bot MCP ไม่ available ใน session นี้**

- `mcp__line-bot__push_text_message` ไม่ปรากฏใน deferred tool list → LINE notifications ถูกข้ามทั้งหมดในรันนี้

- ถ้า LINE Bot MCP ไม่ available → log ไว้ใน summary แล้วดำเนินการต่อ (ไม่ block workflow)



**2026-05-31 — notion-query-database-view ส่ง result ขนาดใหญ่ → ต้องใช้ PowerShell parse**

- result มี 56K+ characters ซึ่งเกิน context limit → ถูก save ลงไฟล์อัตโนมัติ

- แก้ด้วย PowerShell อ่านไฟล์จาก tool-results path แล้ว parse JSON เอง

- ข้อมูลซ้อนอยู่ใน outer array: `$outer[0].text` → parse อีกรอบเป็น inner JSON จึงจะได้ `results[]`

- Properties ใน result เป็น flat object (ไม่ใช่ nested `properties` key) → access ตรงจาก root ได้เลย เช่น `$r.'Task ID'`, `$r.Status`

- `page_id` derive จาก URL: split `/` เอา last segment (32 hex chars) แล้วใส่ dash ตาม UUID format



**2026-05-31 — Mobile repo ไม่อยู่ใน GitHub folder ที่ mount**

- connect-x-mpi เป็น Next.js app (ไม่ใช่ Flutter/React Native mobile)

- Mobile app codebase หลักไม่ถูก mount → วิเคราะห์จาก desktop reference + Figma + requirements แทน

- Task ที่ Status = "Wait Test PR" ยังคง process ได้ เพราะ dev ทำเสร็จแล้ว comment เป็น QA guide



**2026-06-04 — LINE Notification Routing ตาม Issue Type**

- Bug และ Inquiry → ส่งไปกลุ่ม `Cff593dd16c465d61ee5c0a3e9776dcf1`

- Task / Story / อื่นๆ → ส่งไปกลุ่ม `Cf53cc4458d4ad0b33e9c54d5e630c2a3`

- `mcp__line-bot__push_text_message` สามารถใช้ได้โดยตรงใน scheduled session (ไม่ต้อง spawn Code task)



---



### สรุปผลหลังรัน



แจ้งให้รู้ว่า:

- Task ที่ comment ใหม่ไปกี่ task (พร้อมชื่อ) และ link

- Task ที่ข้ามเพราะ AI Analyzed = "Done" หรืออยู่ใน processed_tasks.json แล้วกี่ task

- Task ที่ข้ามเพราะ Status = Done/Production/Wait Test Production กี่ task

- Task ที่ requirement < 80% และ tag SD/Reporter ไปกี่ task (พร้อมชื่อ) — set "Needs Info"

- Task ที่เป็น "Needs Info" และมี comment ใหม่จาก SD/PO → วิเคราะห์ซ้ำกี่ task (พร้อมผล)

- Task ที่เป็น "Needs Info" แต่ยังไม่มี comment ใหม่ → ข้ามกี่ task

- LINE notifications ที่ยิงไปกี่ครั้ง (แยก ✅ และ ⚠️ และแยก group)

- สิ่งที่เรียนรู้และอัปเดต SKILL.md ในครั้งนี้ (ถ้ามี)