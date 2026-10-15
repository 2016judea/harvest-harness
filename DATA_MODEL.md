# Data model — the ideal version

Written 2026-10-15 from the need alone, before looking at what ships. The buyer is a
burgeoning AI engineer who uses Claude Code and has no harness yet: no CLAUDE.md worth
the name, no skills, sessions that start from zero every time. Their question is
*"how do I get an agent to one-shot my work, and keep getting better at it?"*

## Entities

### Method (one)
| field | question it answers for the buyer |
|---|---|
| thesis | What is the idea, in the author's words, before any files? |
| tenets[] | What rules does the author actually work by, and why each one? |
| loop[] | In what order does work turn into a skill? |
| ux_axiom | What does every interface built this way optimise for? |

### Tenet
| field | question |
|---|---|
| number, title | Which rule is this? |
| text | What does it say (verbatim, scrubbed only of private references)? |
| traces_to | Which part of the thesis does it come from? (back-reference) |
| why | What went wrong that made it a rule? |

### Skill
| field | question |
|---|---|
| name | What do I type, or what will trigger it? |
| job | What step of my work does it take over? |
| description | Will it fire when I say the thing I'd actually say? |
| grounded | Was it harvested from real work, and when? Or is it a guess? |
| back_refs[] | Where did each assumption come from, so I can check it? |
| forward_refs[] | Which other skill or tool owns the out-of-scope part? |
| rules[] (text + why) | Where is it strict, and is each rule justified? |
| rule_density | How risky is the domain it covers? |
| kind | Is it a task skill or a tool skill? (tool quirks live in tool skills) |
| files[] | What scripts come with it? |
| tier | Free or paid? |

### Agent
| field | question |
|---|---|
| name, role | Who does the work, and when do I dispatch it? |
| prime_rule | What stops it doing the wrong kind of work (e.g. paperwork instead of building)? |
| gates[] | Where must it stop and hand back to me? |
| memory_policy | What may it remember across runs? |

### Hook
| field | question |
|---|---|
| event | When does it fire (SessionStart, UserPromptSubmit, PreToolUse)? |
| does | What does it put in context or block? |
| why | What failure made it necessary? |
| settings_snippet | How do I wire it in settings.json? |

### Loop step
| field | question |
|---|---|
| order, name | Where am I in the cycle? |
| who | Is this my move or the agent's? |
| artefact | What file does this step leave behind? |

### Draft skill (the buyer's own — the AI-native step)
| field | question |
|---|---|
| source_session | Which of MY sessions is it harvested from? |
| frontmatter_check | Does it have name, a trigger-rich description, a grounded line? |
| rules_without_why | Which rules will get rationalised around? |
| missing_refs | Which claims are unsourced? |
| verdict | Is it ready, and what is the one fix? |

### Offer
| field | question |
|---|---|
| free[] | What can I take right now without paying? |
| paid[] | What do I get for the price? |
| price | One number, one time. |
| delivery | How do I get the files after paying? |

## Joins
Method 1—n Tenet · Method 1—n Loop step · Skill n—n Skill (refs) · Skill n—1 Tenet
(the rule it applies) · Agent n—n Skill · Hook n—1 Skill (e.g. a hook that loads a
skill) · Draft skill n—1 Method (checked against it) · Offer 1—n Skill/Agent/Hook.

## Reality check (done after the model above)

| field | fillable? | source |
|---|---|---|
| thesis, tenets, loop, ux_axiom | yes | `~/.claude/CLAUDE.md`, verbatim; private references cut and marked `[…]` |
| tenet.why | yes | each tenet carries its incident in the source |
| skill.* | yes, for the skills whose job is generic | `~/.claude/skills/*/SKILL.md` frontmatter + body; personal-domain skills excluded whole |
| skill.back_refs | partly: many point at private memories | kept as a pattern, private targets cut |
| agent.*, hook.* | yes | `~/.claude/agents`, `~/.claude/hooks`, `settings.json` hooks block |
| draft_skill.* | yes, two ways | the `crystallize` skill runs on the buyer's own session inside their Claude Code (their reasoning, their transcript, never leaves their machine); the page's checker scores the result against the method, deterministically, in the browser |
| offer.delivery | yes | Stripe payment link → redirect carries the session id → `/api/download` verifies paid and streams the zip |

Nothing in the model is unfillable. The one choice: the site does **not** call a model
on the buyer's transcript. That would put their private session on our server and a
per-use API bill on ours; their own Claude Code does it better, on their machine.
