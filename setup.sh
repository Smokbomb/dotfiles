#!/usr/bin/env bash
# Dotfiles setup script — Mac/Linux
# Usage: bash setup.sh

set -e

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Setting up dotfiles from: $DOTFILES_DIR"

link_file() {
  local src="$1" dst="$2"
  if [ -L "$dst" ]; then
    echo "  [skip] $dst already symlinked"
  elif [ -f "$dst" ]; then
    mv "$dst" "$dst.bak"
    echo "  [backup] $dst.bak"
    ln -s "$src" "$dst" && echo "  [link] $dst"
  else
    ln -s "$src" "$dst" && echo "  [link] $dst"
  fi
}

# ── Git ──────────────────────────────────────────────────────
link_file "$DOTFILES_DIR/.gitconfig" "$HOME/.gitconfig"

# ── Shell ────────────────────────────────────────────────────
link_file "$DOTFILES_DIR/.zshrc"    "$HOME/.zshrc"
link_file "$DOTFILES_DIR/.zprofile" "$HOME/.zprofile"

# ── Claude Code ──────────────────────────────────────────────
CLAUDE_DIR="$HOME/.claude"
mkdir -p "$CLAUDE_DIR"

link_file "$DOTFILES_DIR/.claude/settings.json" "$CLAUDE_DIR/settings.json"

if [ -f "$DOTFILES_DIR/.claude/keybindings.json" ]; then
  link_file "$DOTFILES_DIR/.claude/keybindings.json" "$CLAUDE_DIR/keybindings.json"
fi

# ── Claude Skills ─────────────────────────────────────────────
SKILLS_SRC="$DOTFILES_DIR/.claude/skills"
SKILLS_DST="$CLAUDE_DIR/skills"
if [ -d "$SKILLS_SRC" ]; then
  if [ -L "$SKILLS_DST" ]; then
    echo "  [skip] $SKILLS_DST already symlinked"
  elif [ -d "$SKILLS_DST" ]; then
    mv "$SKILLS_DST" "$SKILLS_DST.bak"
    echo "  [backup] $SKILLS_DST.bak"
    ln -s "$SKILLS_SRC" "$SKILLS_DST" && echo "  [link] $SKILLS_DST"
  else
    ln -s "$SKILLS_SRC" "$SKILLS_DST" && echo "  [link] $SKILLS_DST"
  fi
fi

echo ""
echo "Done! Run 'git pull' in ~/dotfiles on other machines to sync."
