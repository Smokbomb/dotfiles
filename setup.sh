#!/usr/bin/env bash
# Dotfiles setup script — Mac/Linux
# Usage: bash setup.sh

set -e

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Setting up dotfiles from: $DOTFILES_DIR"

# ── Claude Code ──────────────────────────────────────────────
CLAUDE_DIR="$HOME/.claude"
mkdir -p "$CLAUDE_DIR"

# Symlink settings.json (skip if already a symlink)
if [ -L "$CLAUDE_DIR/settings.json" ]; then
  echo "  [skip] ~/.claude/settings.json already symlinked"
elif [ -f "$CLAUDE_DIR/settings.json" ]; then
  echo "  [backup] ~/.claude/settings.json -> ~/.claude/settings.json.bak"
  mv "$CLAUDE_DIR/settings.json" "$CLAUDE_DIR/settings.json.bak"
  ln -s "$DOTFILES_DIR/.claude/settings.json" "$CLAUDE_DIR/settings.json"
  echo "  [link] ~/.claude/settings.json"
else
  ln -s "$DOTFILES_DIR/.claude/settings.json" "$CLAUDE_DIR/settings.json"
  echo "  [link] ~/.claude/settings.json"
fi

# Symlink keybindings.json if it exists in dotfiles
if [ -f "$DOTFILES_DIR/.claude/keybindings.json" ]; then
  if [ -L "$CLAUDE_DIR/keybindings.json" ]; then
    echo "  [skip] ~/.claude/keybindings.json already symlinked"
  else
    [ -f "$CLAUDE_DIR/keybindings.json" ] && mv "$CLAUDE_DIR/keybindings.json" "$CLAUDE_DIR/keybindings.json.bak"
    ln -s "$DOTFILES_DIR/.claude/keybindings.json" "$CLAUDE_DIR/keybindings.json"
    echo "  [link] ~/.claude/keybindings.json"
  fi
fi

echo ""
echo "Done! Claude Code settings are now synced from dotfiles."
echo "Remember: git pull in ~/dotfiles to get latest settings from other machines."
