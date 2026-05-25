# Dotfiles setup script — Windows (PowerShell)
# Usage: .\setup.ps1  (run as Administrator for symlinks)

$ErrorActionPreference = "Stop"
$DotfilesDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Setting up dotfiles from: $DotfilesDir"

function Link-File($target, $source) {
  if (Test-Path $target -PathType Leaf) {
    $existing = Get-Item $target
    if ($existing.LinkType -eq "SymbolicLink") {
      Write-Host "  [skip] $target already symlinked"; return
    }
    Move-Item $target "$target.bak"
    Write-Host "  [backup] $target.bak"
  }
  New-Item -ItemType SymbolicLink -Path $target -Target $source | Out-Null
  Write-Host "  [link] $target"
}

# ── Git ──────────────────────────────────────────────────────
Link-File "$env:USERPROFILE\.gitconfig" "$DotfilesDir\.gitconfig"

# ── Claude Code ──────────────────────────────────────────────
$ClaudeDir = "$env:USERPROFILE\.claude"
if (-not (Test-Path $ClaudeDir)) { New-Item -ItemType Directory -Path $ClaudeDir | Out-Null }

Link-File "$ClaudeDir\settings.json" "$DotfilesDir\.claude\settings.json"

if (Test-Path "$DotfilesDir\.claude\keybindings.json") {
  Link-File "$ClaudeDir\keybindings.json" "$DotfilesDir\.claude\keybindings.json"
}

Write-Host ""
Write-Host "Done! Run 'git pull' in ~/dotfiles on other machines to sync."
