## Where things live

*Added for the packaged harness, 2026-10-15. Everything above this heading is the
author's own file, cut only where it named private work.*

- `~/.claude/CLAUDE.md` — this file. Always loaded, every project. The method.
- `~/.claude/BUSINESS.md` — the rules for building tools for customers, imported below.
- `~/.claude/skills/<name>/SKILL.md` — global skills. Each carries a `grounded:` line.
- `<repo>/.claude/skills/` — skills only meaningful inside one codebase.
- `~/.claude/agents/<name>.md` — the bench. Skills are *how* the work is done; agents
  are *who* does it.
  - **`eng-lead` is the default.** If you named it, it's decided: build the smallest
    working version and report in a few lines.
  - **`product-lead` is a cheap kill gate**, for when nobody has decided. One
    disqualifying fact or BUILD, three lines.
  - Adjacent ideas either agent notices go as one line into `~/Desktop/ideas/BACKLOG.md`,
    never a new dispatch.
- `~/.claude/agent-memory/<agent>/MEMORY.md` — each agent's own memory, loaded into
  its prompt at start. It records only what cost it a cycle.
- `~/.claude/hooks/` — hooks wired in `settings.json` (see `settings.hooks.json`).
- `~/.claude/projects/<repo>/memory/` — Claude Code's own per-project memory. Keep it
  the only memory store; a second hand-kept one drifts.

`[[name]]` links throughout point at the author's memory notes, which do not ship.
They are left in to show the shape of a back-reference: every claim names where it
came from.

## Business rules

@~/.claude/BUSINESS.md
