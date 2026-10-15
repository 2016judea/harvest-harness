---
name: github-scout
description: Evaluate GitHub before building or picking tooling, and read what's trending. Use whenever we're looking for or thinking about a tool, library, framework, MCP server, agent harness or skill pack to solve something — "is there a tool for X", "what should we use for Y", "before we build this", "is this already solved" — and when the user asks "what's trending on GitHub", "anything new on GitHub", "check trending repos". Also the reader for the weekly trending digest at ~/.claude/github-trending/.
grounded: 2026-10-11 — the user: "whenever we are looking/thinking about tooling to solve something we should evaluate github holistically for a fit and in broader strokes look at the trending repos"
---

# github-scout

Two jobs. The rule that triggers them lives in `~/.claude/CLAUDE.md` ("Tooling: check GitHub first").

## 1. Fit search: a specific need

Before building a tool, or choosing one, search GitHub for the need, not the name of a tool you already know.

```bash
gh search repos "<the need in plain words>" --sort stars --limit 20 \
  --json fullName,description,stargazersCount,pushedAt,license,language
gh search repos "<need>" --sort updated --limit 20 ...   # catches new work stars haven't found yet
gh search code "<distinctive API or file name>" --limit 20  # who already wired the thing we'd wire
```

Run 2–4 phrasings of the need. Then read the latest trending digest (job 2) for anything adjacent.

Judge each candidate on the following facts. Read them; never guess.
- **Alive:** `pushedAt` within ~90 days, and issues get answered (`gh issue list -R o/r --limit 10`).
- **Licence:** `gh repo view o/r --json licenseInfo`. No licence means we can't ship it. AGPL inside a hosted product is a problem.
- **Fit:** read the README and one real source file. Does it do *our* step, or something nearby?
- **Weight:** what it pulls in, and whether it needs an account or key we don't have.

**Output: the decision first** (tenet 7): *use X* / *fork X* / *build it, nearest was X because Y*. One line per candidate under that. Stars measure attention, not fit. Never pick on stars alone.

A good existing repo doesn't kill a build (BUSINESS.md rule 1). It changes **what** we build: we wire it in, and don't rewrite it.

## 2. Trending: the broad sweep

`trending.py` scrapes github.com/trending. No auth is needed, and it writes `~/.claude/github-trending/YYYY-MM-DD-<since>[-lang].md`.

```bash
/usr/bin/python3 ~/.claude/skills/github-scout/trending.py weekly            # or daily / monthly
/usr/bin/python3 ~/.claude/skills/github-scout/trending.py weekly --lang python
```

It runs on its own every Monday at 07:00 via launchd (`~/Library/LaunchAgents/local.github-trending.plist`, weekly + monthly). It writes under `~/.claude`, never under `~/Desktop`, because launchd can't read Desktop. To read it: `ls -t ~/.claude/github-trending | head`.

When you read a digest, name the 1–3 repos that touch **our** live work (agent tooling, skills/memory, data pipelines, maps, the current products), say what each would change, and skip the rest. If an adjacent idea comes up, add it as one line to `~/Desktop/ideas/BACKLOG.md`. Don't dispatch anything for it (tenet 10c).

## Traps
- If the script prints "0 repos parsed", GitHub has changed the trending markup. Fix the regexes in `trending.py`; don't fall back to guessing.
- Trending ranks by stars gained in the period. A spike can come from a launch, a Hacker News post or a bot ring. Check the repo's age and its commit history before you trust the spike.
- `gh search` is rate-limited to 30 requests/min when authenticated. Spread the phrasings out; don't loop over them in a tight burst.
- **Impostor repos ride every trending name.** On 2026-10-11, a search for "reverse engineer anything" returned the real `morluto/rea` (102k stars, MIT, npm `rea-agents`) and also 2–105-star clones that copy its description and offer an "Official free download… Local zip" for Windows. Those clones are malware bait. Install only from the canonical repo's own package (npm/pip name in *its* README), and never run a zip from a clone.
- **REA (`rea-agents`) can't get through bot walls, and its JS analyser looks for Electron.** On 2026-10-11 its headless `capture-browser-scenario` got Redfin's rate-limit page, Zillow's PerimeterX and Realtor's Kasada, and real Chrome in `connect` mode got PerimeterX too. `analyze-javascript-application` found 0 network endpoints in a Next.js bundle, where `grep /graphql/` found the route. The working endpoint came from curl probing. Set `timeout_ms` on every step, or a missing selector hangs the run forever.
