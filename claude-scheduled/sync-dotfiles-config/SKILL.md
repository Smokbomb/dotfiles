---
name: sync-dotfiles-config
description: Sync dotfiles config จาก GitHub ทุกวัน — ดึง commit ใหม่ถ้ามี ถ้าไม่มีก็ข้าม
---

## Dotfiles Config Sync

ตรวจสอบว่า dotfiles repo มี commit ใหม่จาก GitHub หรือไม่ ถ้ามีให้ pull และ apply symlinks ใหม่

---

### ขั้นตอน

**Step 1 — Fetch และเช็ค commit**

รัน:
```
git -C C:\Users\USER\Documents\GitHub\dotfiles fetch origin
git -C C:\Users\USER\Documents\GitHub\dotfiles rev-list HEAD..origin/main --count
```

- ถ้าผลลัพธ์เป็น `0` → รายงานว่า "already up to date" แล้วหยุดทันที ไม่ต้องทำ Step ต่อไป
- ถ้าผลลัพธ์ > 0 → ดำเนิน Step 2

---

**Step 2 — Pull changes**

```
git -C C:\Users\USER\Documents\GitHub\dotfiles pull origin main
```

แสดง commit messages ที่ดึงมาใหม่:
```
git -C C:\Users\USER\Documents\GitHub\dotfiles log --oneline ORIG_HEAD..HEAD
```

---

**Step 3 — Apply symlinks ใหม่ (ถ้ามีไฟล์ใหม่)**

```
powershell -ExecutionPolicy RemoteSigned -File C:\Users\USER\Documents\GitHub\dotfiles\setup.ps1
```

---

### สรุปผลหลังรัน

แจ้งให้รู้ว่า:
- มี commit ใหม่กี่ commit (หรือ "already up to date")
- ไฟล์ที่เปลี่ยนแปลง (ถ้ามี)
- symlink ที่สร้างใหม่ (ถ้ามี)
