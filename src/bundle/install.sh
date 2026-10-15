#!/bin/sh
# Install the harness into ~/.claude. Never overwrites: anything that already exists
# is moved to ~/.claude/.harness-backup-<timestamp>/ first.
#   sh install.sh               skills, agents, hooks, agent memory, CLAUDE.md, BUSINESS.md
#   sh install.sh --wire-hooks  also merge settings.hooks.json into ~/.claude/settings.json
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
DEST="$HOME/.claude"
BACK="$DEST/.harness-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DEST"

place() { # place <relative path>
  src="$HERE/$1"; dst="$DEST/$1"
  if [ -e "$dst" ]; then mkdir -p "$(dirname "$BACK/$1")"; mv "$dst" "$BACK/$1"; echo "  backed up $1"; fi
  mkdir -p "$(dirname "$dst")"; cp -R "$src" "$dst"
}

for d in "$HERE"/skills/*/; do place "skills/$(basename "$d")"; done
for f in "$HERE"/agents/*.md; do place "agents/$(basename "$f")"; done
for f in "$HERE"/hooks/*.py; do place "hooks/$(basename "$f")"; done
for d in "$HERE"/agent-memory/*/; do
  [ -e "$DEST/agent-memory/$(basename "$d")" ] || place "agent-memory/$(basename "$d")"
done
place CLAUDE.md
place BUSINESS.md

if [ "${1:-}" = "--wire-hooks" ]; then
  python3 - "$DEST/settings.json" "$HERE/settings.hooks.json" <<'PY'
import json, sys, os
path, add = sys.argv[1], json.load(open(sys.argv[2]))
cur = json.load(open(path)) if os.path.exists(path) else {}
cur.setdefault("cleanupPeriodDays", add["cleanupPeriodDays"])
hooks = cur.setdefault("hooks", {})
for event, entries in add["hooks"].items():
    have = json.dumps(hooks.get(event, []))
    for e in entries:
        if e["hooks"][0]["command"] not in have:
            hooks.setdefault(event, []).append(e)
json.dump(cur, open(path, "w"), indent=2)
print("  hooks wired into", path)
PY
fi

[ -d "$BACK" ] && echo "Previous files are in $BACK"
echo "Installed. Open Claude Code, do some real work, then type: /crystallize"
