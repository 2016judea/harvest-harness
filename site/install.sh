#!/bin/sh
# Free slice of the harness: four skills into ~/.claude/skills and the method into
# ~/.claude/harness-METHOD.md. Never overwrites; existing skills are skipped.
set -eu
BASE="https://harvest-harness.vercel.app/free"
DEST="$HOME/.claude/skills"
mkdir -p "$DEST"
get() { mkdir -p "$(dirname "$2")"; curl -fsSL "$BASE/$1" -o "$2"; }
for f in crystallize/SKILL.md github-scout/SKILL.md github-scout/trending.py \
         mobile-ui-audit/SKILL.md mobile-ui-audit/audit.py mobile-ui-audit/sim_probe.sh mobile-ui-audit/zoomtest.html \
         tool-skill-template/SKILL.md; do
  skill=${f%%/*}
  if [ -e "$DEST/$skill" ] && [ ! -e "$DEST/$skill/.harvest-harness" ]; then
    echo "  skip $skill (you already have one)"; continue
  fi
  get "skills/$f" "$DEST/$f"; touch "$DEST/$skill/.harvest-harness"
done
chmod +x "$DEST"/github-scout/trending.py "$DEST"/mobile-ui-audit/*.py "$DEST"/mobile-ui-audit/*.sh 2>/dev/null || true
[ -e "$HOME/.claude/harness-METHOD.md" ] || get METHOD.md "$HOME/.claude/harness-METHOD.md"
echo "Installed to $DEST. Read ~/.claude/harness-METHOD.md, do some real work in Claude Code, then type: /crystallize"
