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
    Move-Item $target "$target.bak"
    Write-Host "  [backup] $target.bak"
  }
  cmd /c mklink "$target" "$source" | Out-Null
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

Write-Host ""
Write-Host "Done! Run 'git pull' in dotfiles on other machines to sync."
