---
name: mobile-ui-audit
description: Audit any of the user's sites the way a phone visitor would fail on them — iOS zoom traps, sideways overflow, locked scroll, tap targets, tiny text — on real WebKit and Chromium phone profiles, across every Vercel production alias in one run. Use when he says "the mobile site is broken", "scroll is broken on my phone", "can't get back to the header", "run the UI audit", "test all our sites on mobile", "QA this on a phone", or after any CSS change that touches inputs or layout.
grounded: 2026-10-04 — the brickandmortar.dev "mobile scroll is broken" report, where every emulator scrolled cleanly and the real fault was a 12px address input
---

# Mobile UI audit

One script, two phone engines, every site. Run it before believing an emulator.

    pip install playwright && playwright install webkit chromium
    python ~/.claude/skills/mobile-ui-audit/audit.py --vercel --crawl 4 --json /tmp/audit.json --shots /tmp/shots
    python ~/.claude/skills/mobile-ui-audit/audit.py "https://example.com/" --devices iphone

Exit 1 on any FAIL. `--links` HTTP-checks the order/book/shop/menu links plus 40 others;
`--hop` also audits the first same-origin order/book/shop/menu page one click deep (added
2026-10-06; a site takes ~2 min with both, so shard ~10 processes for 150 sites).
Cross-origin frame errors (Cloudflare Turnstile, booking iframes) are not the site's own JS and stay INFO. `--vercel` reads the team's projects off the API (`VERCEL_TOKEN` and `VERCEL_TEAM_ID` in the environment) and picks the custom domain or the shortest
`<name>.vercel.app`; the team-scoped aliases sit behind Vercel SSO and audit as
a 721px login page with a 200, so the picker skips them.

## The rule this skill exists for

**No text-entry control under 16px on a touch screen.** Mobile Safari scales the
page until a focused `input`, `textarea` or `select` reads 16px and does not scale
back on blur. A 12px field means a 1.33x page, the header off the top-left, and a
visitor who says "scroll is broken." No emulator shows it: headless Chrome,
Playwright WebKit and the iPhone device profiles all auto-zoom nothing, which is
why the audit measures the static property instead of trusting a scrolled page.

Fix shape, by stack (all applied 2026-10-04 and live):

- Hand-written CSS: `@media (pointer:coarse){ input:not([type=checkbox]):not([type=radio]):not([type=file]),textarea,select{font-size:16px !important} }`. `pointer:coarse` means "a finger" and leaves every desktop size alone. `!important` because small sizes often sit on id selectors.
- A plain `font-size: 15px` on inputs: raise it to 16.
- Tailwind: `text-base`, never `text-sm`, on an input.
- **Never** `maximum-scale=1` in the viewport meta. iOS ignores it for pinch but Chrome/Android honours it, so it kills pinch-zoom for the people who need it. The audit WARNs on it.

Checkboxes, radios and file inputs do not trigger the zoom and are excluded.

## What a row means

| Severity | Finding | Why it is that severity |
|---|---|---|
| FAIL | iOS zoom trap | the visitor loses the page (above) |
| FAIL | sideways overflow, unclipped | iOS does not honour `overflow-x:hidden` on body reliably; the page pans |
| FAIL | document locked, no inner scroller | content below the fold is unreachable |
| FAIL | page error, HTTP ≥ 400, did not load | nothing to audit |
| FAIL | page renders blank (<40 chars of visible text after load) | the visitor sees nothing |
| FAIL | sideways overflow that **pans** (`panX` > 0 after `scrollTo(400,0)`) | reproduced, not inferred; a leak that does not pan is WARN |
| FAIL | dead link (`--links`): ≥ 400 on two GETs | 401/403/429/503/999 are `blocked` (a bot wall), never reported dead. **Tap it before believing it**: restaurant menu tabs (SpotHopper/BentoBox-style) 404 on GET but JS swaps the tab on click (2026-10-06) |
| WARN | wrong phone keyboard: an email/phone field declared `type=text` | the letters keyboard comes up for a number |
| WARN | autofill disabled: `autocomplete=off` on a name/email/phone/address/card field | autofill reads `autocomplete`; off kills it |
| WARN | broken image (complete, `naturalWidth` 0) | visible hole on the page |
| WARN | tap target under 24px | WCAG 2.5.8 minimum; Apple asks 44 |
| WARN | text under 12px | a count, not a verdict |
| WARN | fixed/sticky layer covering ≥ 40% | usually a modal or a hero card; check it dismisses. The 'document locked' FAIL fires on the same pages while the modal is open: 49 overlay + 20 locked rows in the 2026-10-06 sweep of 150 sites, and all 5 tapped by hand closed and scrolled after the close tap |
| WARN | header not at y=0 after a scroll round-trip | a sticky or anchor is fighting the scroll |
| WARN | viewport meta caps zoom | see above |
| INFO | scroll model, weight, inner scrollers | context for reading the rest |

The "wide element" check only counts elements no ancestor clips before `body`,
so a 960px table inside a `.tscroll{overflow-x:auto}` is not a finding. A naive
rect check flagged 36 such pages on `/` before that filter existed.

## When the audit says ok and the phone still disagrees

That is exactly the 2026-10-04 shape. The next tier is a real Mobile Safari, and
it exists on this Mac now: **a headless iOS 27 simulator driven by `sim_probe.sh`**
in this directory. Same evening it reproduced the bug the emulators could not —
`evidence/2026-10-04-prefix-zoomed-1.33.png` is the pre-fix `/` after tapping the
address field and closing the keyboard (scale 1.33, header gone, right edge
clipped); `evidence/2026-10-04-fixed-scale-1.png` is the shipped fix, focused at
scale 1.00 with the keyboard up; `evidence/2026-10-04-control-stays-1.33.png` is
`zoomtest.html`, a 12px field whose page prints `visualViewport.scale`.

    ~/.claude/skills/mobile-ui-audit/sim_probe.sh "<url>" /tmp/out 201 369   # tap in points

What it took, so nobody re-learns it:
- Xcode 27 from the Mac App Store is ~3.7 GB on disk when complete and ships **no
  Simulator.app** anywhere; `xcodebuild`, `simctl` and headless rendering all work
  without it. `mas install` needs sudo; the App Store GUI was scripted instead
 .
- iOS runtime: `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcodebuild -downloadPlatform iOS`
  (8 GB). It ends with a "manifest couldn't be opened" registration error and the
  runtime is registered anyway; iPhone 17 devices appear.
- Taps: `brew trust facebook/fb && brew install idb-companion`; `pip install fb-idb`. `idb connect <udid>` again after every boot. Coordinates are
  points; measure a field with Playwright WebKit at 402x874 and tap its rect centre.
  The first `openurl` after a boot times out; the second lands.
- The software keyboard appears headless, so the focus zoom runs. The first control
  tap that "did nothing" was a dead companion after a reboot, not a missing keyboard.
- Playwright WebKit cannot stand in for this: it does not auto-zoom. Chrome and
  Android never zoom on focus at all, which is why the Android visitor never saw it.

Other tiers: your own iPhone on USB with Safari's Develop menu (needs him);
BrowserStack/LambdaTest real devices (spends money, a gate).

Also wired 2026-10-04, user scope, in `~/.claude.json`: the `playwright` MCP
(`@playwright/mcp --browser webkit --device "iPhone 13"`: accessibility snapshots,
taps, screenshots on WebKit) and `chrome-devtools` MCP (performance traces,
console, network). **If the playwright MCP errors that its browser is missing**, run
`npx -y @playwright/mcp install-browser webkit` (78 MB, ~1 min); a cache clear or an
`@latest` bump leaves the config pointing at a WebKit build that is not on disk. Fixed
that way 2026-10-05. Use them for interactive poking; `audit.py` for the sweep;
`sim_probe.sh` for the one thing only real iOS shows.

