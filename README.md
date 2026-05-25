# dotfiles

Personal dotfiles — syncs Claude Code settings across Mac, Windows, and Linux.

## What's synced

| File | Purpose |
|------|---------|
| `.claude/settings.json` | Claude Code permissions & hooks |
| `.claude/keybindings.json` | Custom keyboard shortcuts (create when needed) |

## Setup on a new machine

### Mac / Linux
```bash
git clone https://github.com/Smokbomb/dotfiles.git ~/dotfiles
bash ~/dotfiles/setup.sh
```

### Windows (PowerShell — run as Administrator)
```powershell
git clone https://github.com/Smokbomb/dotfiles.git $env:USERPROFILE\dotfiles
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
~\dotfiles\setup.ps1
```

## Workflow ข้ามเครื่อง

1. **ก่อน switch เครื่อง** — push project code + push dotfiles ถ้า settings เปลี่ยน
2. **หลัง switch เครื่อง** — `git pull` ใน `~/dotfiles` แล้วทำงานต่อได้เลย

## Project context (CLAUDE.md)

แต่ละ project มี `CLAUDE.md` อยู่ใน repo นั้นเลย — sync อัตโนมัติผ่าน git push/pull
ไม่ต้อง setup เพิ่ม

## Mobile

ใช้ Claude.ai บนมือถือสำหรับ review code / วางแผน
เปิด GitHub เพื่อดู code และ CLAUDE.md ของแต่ละ project
