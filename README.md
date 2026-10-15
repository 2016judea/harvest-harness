# Harvest Harness

**Live:** https://harvest-harness.vercel.app

> 4. Sell your AI/harness/claude config somehow to burgeoning AI engineers.

Aidan's Claude Code harness, packaged. The asset is the method that produces skills:
work a novel problem in a session → verify it in the world → `/crystallize` → a skill
with rules that carry their why, a `grounded:` line, back-references for every
assumption and forward-references to the tools it doesn't own. Next time is one-shot.

## Free

`free/` is the public slice, also served by the site:

    curl -fsSL https://harvest-harness.vercel.app/install.sh | sh

- `free/METHOD.md`: the thesis and operating tenets, verbatim, with private references cut and marked `[…]`
- `crystallize`, `github-scout`, `mobile-ui-audit`, `tool-skill-template`

The site also checks any `SKILL.md` you paste against the method (description triggers,
grounded line, rules with a why, back- and forward-references), in the browser.

## Paid, $49 once

The full bench: `CLAUDE.md` with all 14 tenets, `BUSINESS.md`, the `eng-lead` and
`product-lead` agents with memory seeds, three hooks and the `settings.json` block,
twelve skills, and `install.sh`. A Stripe payment link redirects to `/thanks.html`
with the Checkout Session id; `/api/download` checks the session is paid and came
from that link, then streams the zip, which is bundled inside the function and never
committed here.

## How it's built

`scripts/build.py` copies from `~/.claude` by **whitelist** (named skills, files,
agents, hooks), applies a substitution table where an `old` string that is missing
fails the build, then scans every shipped file against a deny list (paths, account
ids, keys, emails, phone numbers, personal-domain words). One hit fails the build.

    python3 scripts/build.py      # free/, private/harness.zip, build/
    python3 scripts/deploy.py     # needs VERCEL_TOKEN, VERCEL_TEAM_ID

Vercel env: `STRIPE_SECRET_KEY`, `PAYMENT_LINK_ID`. `DATA_MODEL.md` is the ideal
model this was built against.

MIT for the code and the free slice. Not affiliated with Anthropic.
