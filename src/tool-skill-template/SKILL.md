---
name: tool-skill-template
description: Template for a TOOL skill — one per API, CLI or service your agent keeps fighting. Copy this folder to ~/.claude/skills/<tool-name>/, rename, and fill it from a session where the tool actually bit you. Use when you say "make a skill for <tool>", "the <API> keeps breaking", "write down how <service> works", or when crystallize says a lesson belongs in a tool skill.
grounded: 2026-10-15 — distilled from the shape of the `vercel-api` and `reddit-mining` tool skills in the full harness; contains no instance of its own until you fill it
---

# <Tool name>

<!-- One line: what this tool is for, in the words you'd type. Task skills point
here instead of restating any of this (tenet 6: every tool gets its own skill). -->

## Credentials and where they live

<!-- The env var name and the FILE it is read from, never the value.
     Example: `API_TOKEN` in `./.env`. Every call needs `team=<id>` or it sees nothing. -->

## The calls that work

<!-- The 3–6 calls you actually use, copy-pasteable. Only ones you ran.
     Each with what it returns and the one field that matters. -->

    GET https://api.example.com/v1/things?team=<id>

## The fields that lie

<!-- The highest-value section. Every entry: what it says, what is true, the date
     you found out, and the tell that spots it. A green status over nothing, a
     200 that is a login page, a count that silently caps. -->

- **<field or status>** says X; really Y. Found <YYYY-MM-DD> when <what broke>.
  Tell: <the one check that catches it>.

## Limits

<!-- Rate limits, quotas, reset times, size caps — with the error code you saw. -->

## Rules (only where a mistake is expensive)

<!-- Rule density follows risk (tenet 5). Every rule carries its why:
     **Never X.** Why: on <date>, X did <cost>. -->

## What this skill does not own

<!-- Forward-reference the neighbours (tenet 4). One line each:
     Visit counts → `site-analytics`. Phone QA → `mobile-ui-audit`. -->
