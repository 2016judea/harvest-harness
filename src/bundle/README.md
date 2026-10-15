# The harness

Aidan's Claude Code setup, scrubbed of everything private: the method, the bench,
the hooks, and the skills that are not about his own life.

## Install

    sh install.sh               # skills, agents, hooks, CLAUDE.md, BUSINESS.md
    sh install.sh --wire-hooks  # also wire the hooks into ~/.claude/settings.json

Nothing is overwritten. Anything already at a path moves to
`~/.claude/.harness-backup-<timestamp>/` first.

## What's here

| path | what it is |
|---|---|
| `CLAUDE.md` | The method: thesis, 14 operating tenets, the loop, the UX axiom, grounding dates, and the always-on rules that wire the bench. Loads in every session. |
| `BUSINESS.md` | Five rules for building tools for customers. Imported by CLAUDE.md. |
| `agents/eng-lead.md` | The default agent. Builds the smallest working version and reports in a few lines. |
| `agents/product-lead.md` | A cheap kill gate. One disqualifying fact, or BUILD. |
| `agent-memory/*/MEMORY.md` | Empty seeds for each agent's own memory, with the rule for what belongs in it. |
| `hooks/pending.py` | SessionStart: surfaces due follow-ups from `~/.claude/pending.json` in-session. |
| `hooks/skill_on_keyword.py` | UserPromptSubmit: loads a skill whenever a prompt matches a pattern. |
| `hooks/send_cap.py` | PreToolUse: refuses a mail send past an hourly or daily cap. Written for a Zoho MCP; change `TOOLS` for yours. |
| `settings.hooks.json` | The hooks block for `settings.json`. |
| `skills/` | 12 skills. Each has a `grounded:` line: the date and the real session it came from. |

## Where to start

1. Do a real piece of work in Claude Code until it works.
2. Type `/crystallize`. It reads the session you just had and writes your first skill
   from it: the wrong turn, the rule and its why, the trigger phrases you'd use.
3. Next time you say those words, the skill fires and the work is one-shot.

`[[name]]` links point at the author's memory notes, which don't ship. They're left
in to show what a back-reference looks like.

Licence: MIT for your own use. Please don't resell the bundle.
