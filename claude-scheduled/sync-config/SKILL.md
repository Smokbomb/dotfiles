---
name: sync-config
description: sync config ai
---

ตรวจสอบ dotfiles repo ว่ามี commit ใหม่จาก GitHub ไหม
1. รัน: git -C C:\Users\USER\Documents\GitHub\dotfiles fetch origin
2. รัน: git -C C:\Users\USER\Documents\GitHub\dotfiles rev-list HEAD..origin/main --count
   - ถ้าได้ 0 → รายงาน "already up to date" แล้วหยุด
   - ถ้า > 0 → ทำขั้นตอนต่อไป
3. รัน: git -C C:\Users\USER\Documents\GitHub\dotfiles pull origin main
4. รัน: powershell -ExecutionPolicy RemoteSigned -File C:\Users\USER\Documents\GitHub\dotfiles\setup.ps1
5. รายงานสรุป: commit ที่ดึงมา + symlinks ที่สร้างใหม่