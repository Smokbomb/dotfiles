# Dotfiles setup script — Windows (PowerShell)
# Usage: .\setup.ps1  (run as Administrator for symlinks)

$ErrorActionPreference = "Stop"
$DotfilesDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Setting up dotfiles from: $DotfilesDir"

# ── Claude Code ──────────────────────────────────────────────
$ClaudeDir = "$env:USERPROFILE\.claude"
if (-not (Test-Path $ClaudeDir)) { New-Item -ItemType Directory -Path $ClaudeDir | Out-Null }

function Link-File($target, $source) {
  if (Test-Path $target -PathType Leaf) {
    $existing = Get-Item $target
    if ($existing.LinkType -eq "SymbolicLink") {
      Write-Host "  [skip] $target already symlinked"
      return
    }
    Move-Item $target "$target.bak"
    Write-Host "  [backup] $target.bak"
  }
  New-Item -ItemType SymbolicLink -Path $target -Target $source | Out-Null
  Write-Host "  [link] $target"
}

Link-File "$ClaudeDir\settings.json" "$DotfilesDir\.claude\settings.json"

$keybindings = "$DotfilesDir\.claude\keybindings.json"
if (Test-Path $keybindings) {
  Link-File "$ClaudeDir\keybindings.json" $keybindings
}

Write-Host ""
Write-Host "Done! Claude Code settings are now synced from dotfiles."
Write-Host "Remember: git pull in ~/dotfiles to get latest settings from other machines."
