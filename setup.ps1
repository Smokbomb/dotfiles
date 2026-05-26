# Dotfiles setup script — Windows (PowerShell)
# Usage: .\setup.ps1  (requires Developer Mode ON in Settings)

$ErrorActionPreference = "Stop"
$DotfilesDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Setting up dotfiles from: $DotfilesDir"

function Link-File($target, $source) {
  if (Test-Path $target) {
    $existing = Get-Item $target -Force
    if ($existing.LinkType -eq "SymbolicLink") {
      Write-Host "  [skip] $target already symlinked"; return
    }
    Move-Item $target "$target.bak" -Force
    Write-Host "  [backup] $target.bak"
  }
  $result = cmd /c mklink "$target" "$source" 2>&1
  if ($LASTEXITCODE -ne 0) { Write-Host "  [error] $result"; return }
  Write-Host "  [link] $target"
}

function Link-Dir($target, $source) {
  if (Test-Path $target) {
    $existing = Get-Item $target -Force
    if ($existing.LinkType -eq "SymbolicLink" -or $existing.LinkType -eq "Junction") {
      Write-Host "  [skip] $target already linked"; return
    }
    Move-Item $target "$target.bak"
    Write-Host "  [backup] $target.bak"
  }
  cmd /c mklink /D "$target" "$source" | Out-Null
  Write-Host "  [link] $target"
}

# ── Git ──────────────────────────────────────────────────────
if (Test-Path "$DotfilesDir\.gitconfig") {
  Link-File "$env:USERPROFILE\.gitconfig" "$DotfilesDir\.gitconfig"
}

# ── Claude Code ──────────────────────────────────────────────
$ClaudeDir = "$env:USERPROFILE\.claude"
if (-not (Test-Path $ClaudeDir)) { New-Item -ItemType Directory -Path $ClaudeDir | Out-Null }

Link-File "$ClaudeDir\settings.json" "$DotfilesDir\.claude\settings.json"

if (Test-Path "$DotfilesDir\.claude\keybindings.json") {
  Link-File "$ClaudeDir\keybindings.json" "$DotfilesDir\.claude\keybindings.json"
}

# ── Claude Skills ─────────────────────────────────────────────
if (Test-Path "$DotfilesDir\.claude\skills") {
  Link-Dir "$ClaudeDir\skills" "$DotfilesDir\.claude\skills"
}

# ── Claude Desktop / Cowork preferences ──────────────────────
$AppData = $env:APPDATA
Link-File "$AppData\Claude\claude_desktop_config.json" "$DotfilesDir\claude_desktop_config.json"

# ── Scheduled Task SKILL.md files ────────────────────────────
$ScheduledSrc = "$DotfilesDir\claude-scheduled"
$ScheduledDst = "$env:USERPROFILE\Documents\Claude\Scheduled"
if (Test-Path $ScheduledSrc) {
  if (-not (Test-Path "$env:USERPROFILE\Documents\Claude")) {
    New-Item -ItemType Directory -Path "$env:USERPROFILE\Documents\Claude" | Out-Null
  }
  Link-Dir $ScheduledDst $ScheduledSrc
}

# ── Cowork Space scheduled-tasks.json ────────────────────────
$AccountId = "e7cba526-6f76-443c-a20f-4b01c2066a74"
$SpacesBase = "$AppData\Claude\local-agent-mode-sessions\$AccountId"
Get-ChildItem "$DotfilesDir\cowork-spaces" -Directory | ForEach-Object {
  $spaceId = $_.Name
  $spaceDir = "$SpacesBase\$spaceId"
  if (-not (Test-Path $spaceDir)) { New-Item -ItemType Directory -Path $spaceDir | Out-Null }
  Link-File "$spaceDir\scheduled-tasks.json" "$DotfilesDir\cowork-spaces\$spaceId\scheduled-tasks.json"
}

Write-Host ""
Write-Host "Done! Run 'git pull' in dotfiles on other machines to sync."
