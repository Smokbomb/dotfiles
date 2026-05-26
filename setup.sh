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

# ── Claude Desktop / Cowork preferences ──────────────────────
MAC_CLAUDE_APP="$HOME/Library/Application Support/Claude"
mkdir -p "$MAC_CLAUDE_APP"
link_file "$DOTFILES_DIR/claude_desktop_config.json" "$MAC_CLAUDE_APP/claude_desktop_config.json"

# ── Scheduled Task SKILL.md files ────────────────────────────
mkdir -p "$HOME/Documents/Claude"
SCHEDULED_DST="$HOME/Documents/Claude/Scheduled"
if [ -d "$DOTFILES_DIR/claude-scheduled" ]; then
  if [ -L "$SCHEDULED_DST" ]; then
    echo "  [skip] $SCHEDULED_DST already symlinked"
  elif [ -d "$SCHEDULED_DST" ]; then
    mv "$SCHEDULED_DST" "$SCHEDULED_DST.bak"
    echo "  [backup] $SCHEDULED_DST.bak"
    ln -s "$DOTFILES_DIR/claude-scheduled" "$SCHEDULED_DST" && echo "  [link] $SCHEDULED_DST"
  else
    ln -s "$DOTFILES_DIR/claude-scheduled" "$SCHEDULED_DST" && echo "  [link] $SCHEDULED_DST"
  fi
fi

# ── Cowork Space scheduled-tasks.json ────────────────────────
ACCOUNT_ID="e7cba526-6f76-443c-a20f-4b01c2066a74"
SPACES_BASE="$MAC_CLAUDE_APP/local-agent-mode-sessions/$ACCOUNT_ID"
for space_dir in "$DOTFILES_DIR/cowork-spaces"/*/; do
  SPACE_ID="$(basename "$space_dir")"
  DST_DIR="$SPACES_BASE/$SPACE_ID"
  mkdir -p "$DST_DIR"
  SRC="$DOTFILES_DIR/cowork-spaces/$SPACE_ID/scheduled-tasks.json"
  DST="$DST_DIR/scheduled-tasks.json"
  # Copy with Mac path substitution (Windows paths → Mac paths)
  sed "s|C:\\\\Users\\\\USER\\\\Documents|$HOME/Documents|g; s|\\\\|/|g" "$SRC" > "$DST"
  echo "  [copy+fix] $DST"
done

# ── Claude Scheduled Tasks ────────────────────────────────────
if [ -d "$DOTFILES_DIR/.claude/scheduled-tasks" ]; then
  if [ -L "$CLAUDE_DIR/scheduled-tasks" ]; then
    echo "  [skip] $CLAUDE_DIR/scheduled-tasks already symlinked"
  elif [ -d "$CLAUDE_DIR/scheduled-tasks" ]; then
    mv "$CLAUDE_DIR/scheduled-tasks" "$CLAUDE_DIR/scheduled-tasks.bak"
    echo "  [backup] $CLAUDE_DIR/scheduled-tasks.bak"
    ln -s "$DOTFILES_DIR/.claude/scheduled-tasks" "$CLAUDE_DIR/scheduled-tasks" && echo "  [link] $CLAUDE_DIR/scheduled-tasks"
  else
    ln -s "$DOTFILES_DIR/.claude/scheduled-tasks" "$CLAUDE_DIR/scheduled-tasks" && echo "  [link] $CLAUDE_DIR/scheduled-tasks"
  fi
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
