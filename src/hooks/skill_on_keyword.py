#!/usr/bin/env python3
"""UserPromptSubmit hook: when the prompt matches a pattern, print a skill so it is in
context before any reasoning starts. stdout of a UserPromptSubmit hook is added as context.

Why this exists: a skill that must apply EVERY time a topic comes up cannot rely on the
model choosing to invoke it. The original loaded a distribution-channel skill whenever a
prompt was about sending something to a person (2026-09-25: "i want the skill natively
loaded anytime we are reasoning on sending something please").

Edit RULES: (regex, skill name). First match wins. Fails silent and open.
"""
import json, re, sys, pathlib

RULES = [
    (r"\b(send|sending|email|outreach|reach out|cold|pitch|dm|campaign|follow[- ]?up)\b", "distribution-channel"),
    (r"\b(journal this|make a skill|crystallize|capture this)\b", "crystallize"),
]

try:
    prompt = json.load(sys.stdin).get("prompt", "")
except Exception:
    sys.exit(0)
for pat, name in RULES:
    if re.search(pat, prompt, re.I):
        skill = pathlib.Path.home() / ".claude/skills" / name / "SKILL.md"
        if skill.exists():
            print(f"<{name}-skill note='auto-loaded by ~/.claude/hooks/skill_on_keyword.py'>")
            print(skill.read_text())
            print(f"</{name}-skill>")
        break
