#!/usr/bin/env python3
"""Build the harness from ~/.claude, scrubbed, by WHITELIST.

Writes:
  free/                 the public slice (committed): METHOD.md + 4 skills
  private/harness/      the paid bench (gitignored), and private/harness.zip
  build/                the deploy staging dir: site/ + free/ + api/_bundle.js

Nothing reaches free/ or private/ unless it is named in FREE_SKILLS, PAID_SKILLS,
AGENTS, HOOKS or a src/ file. Every text file is then passed through the
substitution table and the DENY check; one hit fails the whole build.
"""
import base64, io, json, re, shutil, sys, zipfile
from pathlib import Path

HOME = Path.home() / ".claude"
ROOT = Path(__file__).resolve().parent.parent
FREE, PRIV, BUILD, SRC = ROOT / "free", ROOT / "private", ROOT / "build", ROOT / "src"

# skill -> files inside it that may ship (everything else is left behind)
FREE_SKILLS = {
    "crystallize": ["SKILL.md"],
    "github-scout": ["SKILL.md", "trending.py"],
    "mobile-ui-audit": ["SKILL.md", "audit.py", "sim_probe.sh", "zoomtest.html"],
}
PAID_SKILLS = {
    **FREE_SKILLS,
    "reframe": ["SKILL.md"],
    "think-big": ["SKILL.md"],
    "beautify": ["SKILL.md"],
    "claude-usage-mining": ["SKILL.md"],
    "mac-menu-bar-app": ["SKILL.md"],
    "build-remote-mcp-server": ["SKILL.md", "scripts/mcp_http_smoke_test.py"],
    "reddit-mining": ["SKILL.md", "scripts/reddit_pull.py"],
    "vercel-api": ["SKILL.md"],
}
AGENTS = ["eng-lead.md", "product-lead.md"]
HOOKS = {"pending.py": "pending.py", "channel_skill.py": "skill_on_keyword.py",
         "zoho_send_cap.py": "send_cap.py"}

# The substitution table, deny list and drop list live OUTSIDE this public repo: they
# name exactly the strings that must not ship. Path overridable with SCRUB_RULES.
import importlib.util, os
_rp = Path(os.environ.get("SCRUB_RULES") or Path.home() / ".claude/harvest-harness/scrub_rules.py")
if not _rp.exists():
    sys.exit(f"scrub rules not found at {_rp}; refusing to build without them")
_spec = importlib.util.spec_from_file_location("scrub_rules", _rp)
_rules = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_rules)
GLOBAL, PER, DROP_SECTIONS = _rules.GLOBAL, _rules.PER, _rules.DROP_SECTIONS
DENY, EMAIL, EMAIL_OK, ALLOW_LINES = _rules.DENY, _rules.EMAIL, _rules.EMAIL_OK, _rules.ALLOW_LINES


def drop_sections(text: str, heads: list[str], key: str) -> str:
    for h in heads:
        i = text.find("\n" + h + "\n")
        if i < 0:
            sys.exit(f"DROP heading not found in {key}: {h}")
        level = len(h) - len(h.lstrip("#"))
        rest = text[i + 1 + len(h):]
        m = re.search(r"\n#{1,%d} " % level, rest)
        text = text[:i + 1] + (rest[m.start() + 1:] if m else "")
    return text


def scrub(key: str, text: str) -> str:
    text = drop_sections(text, DROP_SECTIONS.get(key, []), key)
    for old, new in GLOBAL:
        text = re.sub(old, new, text)
    for old, new in PER.get(key, []):
        if old not in text:
            sys.exit(f"PER substitution not found in {key}: {old[:70]!r}")
        text = text.replace(old, new)
    return text


def deny_hits(name: str, text: str) -> list[str]:
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if line.strip() in ALLOW_LINES:
            continue
        for pat in DENY:
            if re.search(pat, line):
                out.append(f"{name}:{i}: /{pat}/ {line.strip()[:110]}")
        for e in EMAIL.findall(line):
            if e not in EMAIL_OK and not e.endswith("example.com"):
                out.append(f"{name}:{i}: email {e}")
    return out


# ------------------------------------------------------------------- the method
def method_text() -> str:
    src = (HOME / "CLAUDE.md").read_text()
    lines = src.splitlines(keepends=True)

    def block(start: str, end: str) -> str:
        a = src.index(start)
        b = src.index(end, a)
        return src[a:b]

    tenets = block("## Operating tenets", "## The loop")
    # tenets 12 and 13 are about sending things to people through channels that do not ship
    t12 = tenets.index("12. **I draft what goes to a person")
    t14 = tenets.index("14. **An approved prototype ships verbatim.**")
    tenets = tenets[:t12] + "[Tenets 12 and 13, on drafting and sending to real people, are in the full bench.]\n\n" + tenets[t14:]
    tenets, n = re.subn(r"\n   \(`[a-z-]+` under `[a-z-]+` is the pattern\.\)\n", "\n   […]\n", tenets)
    assert n == 1, "tenet 6 example line moved"
    head = (
        src[:src.index("## Operating tenets")]
        + tenets
        + block("## The loop", "## The UX axiom")
        + block("## The UX axiom", "## The philosophy")
        + block("## Grounding dates", "## Tooling: check GitHub first")
    )
    return head.rstrip() + "\n"


def claude_md_template() -> str:
    """The paid CLAUDE.md: the method, plus the always-on rules that wire the bench."""
    src = (HOME / "CLAUDE.md").read_text()
    a, b = src.index("## Tooling: check GitHub first"), src.index("## Where things live")
    extra = src[a:b]
    cut_a = extra.index("**Why:** *\"Just because someone")
    cut_b = extra.index("**Not for pages about us.**")
    extra = extra[:cut_a] + "**Why:** *\"Just because someone didn't respond to my email, doesn't mean they\naren't using the thing.\"* […] Silence in the inbox is not a no, but a dark site\ncan't tell you either way.\n\n" + extra[cut_b:]
    extra = extra.replace("(bricks'\nPostHog)", "(PostHog)")
    extra = extra.replace(", pointing at `2016judea/rsra-draft`", "")
    m = method_text().replace("[Tenets 12 and 13, on drafting and sending to real people, are in the full bench.]\n\n", "")
    t = src.index("12. **I draft what goes to a person")
    t14 = src.index("14. **An approved prototype ships verbatim.**")
    t1213 = src[t:t14]
    t1213 = t1213.replace("**Write it in his voice with the `aidan-voice` skill**, which is measured off\n    51,380 words of his own Substack rather than impressions of it",
                          "**Write it in his voice** — a voice skill measured off his own writing,\n    not impressions of it")
    t1213 = t1213.replace("the\n    `distribution-channel` skill is loaded, and the channel", "the\n    channel")
    t1213 = t1213.replace(" A hook (`~/.claude/hooks/channel_skill.py`) injects it whenever a\n    prompt mentions sending; if it did not fire, invoke it by hand.",
                          " A hook (`hooks/skill_on_keyword.py`) can inject a channel skill whenever a\n    prompt mentions sending.")
    m = m.replace("14. **An approved prototype ships verbatim.**", t1213 + "14. **An approved prototype ships verbatim.**")
    tail = (SRC / "bundle" / "WHERE_THINGS_LIVE.md").read_text()
    return m.rstrip() + "\n\n" + extra.rstrip() + "\n\n" + tail


# ----------------------------------------------------------------------- build
def write(dst: Path, text: str):
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text)


def copy_skills(skills: dict, out: Path):
    for name, files in skills.items():
        for f in files:
            raw = (HOME / "skills" / name / f).read_text()
            write(out / "skills" / name / f, scrub(f"skills/{name}/{f}", raw))
        if name in ("mobile-ui-audit", "github-scout"):
            for f in files:
                if f.endswith((".py", ".sh")):
                    (out / "skills" / name / f).chmod(0o755)
    write(out / "skills" / "tool-skill-template" / "SKILL.md", (SRC / "tool-skill-template" / "SKILL.md").read_text())


def main():
    for d in (FREE, PRIV, BUILD):
        shutil.rmtree(d, ignore_errors=True)

    # free slice
    write(FREE / "METHOD.md", method_text())
    copy_skills(FREE_SKILLS, FREE)

    # paid bench
    H = PRIV / "harness"
    copy_skills(PAID_SKILLS, H)
    write(H / "CLAUDE.md", claude_md_template())
    write(H / "BUSINESS.md", scrub("BUSINESS.md", (HOME / "BUSINESS.md").read_text()))
    for a in AGENTS:
        write(H / "agents" / a, scrub(f"agents/{a}", (HOME / "agents" / a).read_text()))
    for f in (SRC / "bundle").rglob("*"):
        if f.is_file() and f.name != "WHERE_THINGS_LIVE.md":
            write(H / f.relative_to(SRC / "bundle"), f.read_text())
    for src_name, dst_name in HOOKS.items():
        over = SRC / "hooks" / dst_name
        text = over.read_text() if over.exists() else scrub(f"hooks/{src_name}", (HOME / "hooks" / src_name).read_text())
        write(H / "hooks" / dst_name, text)
    for p in [H / "install.sh", *(H / "hooks").glob("*.py")]:
        p.chmod(0o755)

    # scrub check over everything that will leave this machine
    hits = []
    shipped = [p for p in [*FREE.rglob("*"), *H.rglob("*")] if p.is_file()]
    for p in shipped:
        hits += deny_hits(str(p.relative_to(ROOT)), p.read_text())
    if hits:
        print("\n".join(hits))
        sys.exit(f"SCRUB FAILED: {len(hits)} hits")

    # zip
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(H.rglob("*")):
            if p.is_file():
                zi = zipfile.ZipInfo(str(Path("harness") / p.relative_to(H)), (2026, 10, 15, 0, 0, 0))
                zi.external_attr = (0o755 if p.stat().st_mode & 0o111 else 0o644) << 16
                zi.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(zi, p.read_bytes())
    (PRIV / "harness.zip").write_bytes(zbuf.getvalue())

    # deploy staging
    shutil.copytree(ROOT / "site", BUILD)
    shutil.copytree(FREE, BUILD / "free")
    write(BUILD / "api" / "_bundle.js", "export const ZIP_B64 = " + json.dumps(base64.b64encode(zbuf.getvalue()).decode()) + ";\n")

    counts = {
        "free_files": sum(1 for p in FREE.rglob("*") if p.is_file()),
        "paid_files": sum(1 for p in H.rglob("*") if p.is_file()),
        "paid_skills": len(list((H / "skills").iterdir())),
        "zip_bytes": len(zbuf.getvalue()),
    }
    write(ROOT / "site" / "counts.json", json.dumps(counts) + "\n")
    shutil.copy(ROOT / "site" / "counts.json", BUILD / "counts.json")
    print(f"scrub: 0 hits across {len(shipped)} shipped files")
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
