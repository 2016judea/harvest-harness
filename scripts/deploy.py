#!/usr/bin/env python3
"""Deploy build/ to Vercel over the REST API. Run scripts/build.py first.
Needs VERCEL_TOKEN and VERCEL_TEAM_ID in the environment. build/api/_bundle.js (the paid zip)
goes up inside the download function only. Enables Web Analytics and prints the aliases."""
import hashlib, os, sys, time
from pathlib import Path
import requests

TEAM, PROJECT = os.environ["VERCEL_TEAM_ID"], "harvest-harness"
BUILD = Path(__file__).resolve().parent.parent / "build"
H = {"Authorization": f"Bearer {os.environ['VERCEL_TOKEN']}"}
API = "https://api.vercel.com"
assert (BUILD / "api" / "_bundle.js").exists(), "run scripts/build.py first"

# Only public/ is static. Until 2026-10-19 every file sat at the deployment root with
# outputDirectory ".", so api/_bundle.js (the paid zip, base64) was a static URL and the
# /api/_bundle redirect matched the raw path only: /api/%5Fbundle.js and /%61pi/_bundle.js
# served the whole $49 harness (curl, 200, 119 KB). Static files now go up under public/;
# api/ and vercel.json stay at the root, where only the download function reads them.
def upload_name(rel):
    if rel.parts[0] == "api" or str(rel) == "vercel.json":
        return str(rel)
    return "public/" + str(rel)


files = []
for p in sorted(BUILD.rglob("*")):
    if not p.is_file() or p.name.startswith("."):
        continue
    b = p.read_bytes(); sha = hashlib.sha1(b).hexdigest()
    r = requests.post(f"{API}/v2/files?teamId={TEAM}", data=b, headers={**H, "x-vercel-digest": sha, "Content-Type": "application/octet-stream"})
    if not r.ok:
        sys.exit(f"upload failed {p}: {r.text[:200]}")
    files.append({"file": upload_name(p.relative_to(BUILD)), "sha": sha, "size": len(b)})
print(f"uploaded {len(files)} files")
d = requests.post(f"{API}/v13/deployments?teamId={TEAM}&forceNew=1", headers=H, json={
    "name": PROJECT, "project": PROJECT, "target": "production", "files": files,
    "projectSettings": {"framework": None, "buildCommand": "echo build", "outputDirectory": "public", "installCommand": "echo skip"},
}).json()
print("deployment", d.get("id"), d.get("readyState"), d.get("error"))
for _ in range(100):
    s = requests.get(f"{API}/v13/deployments/{d['id']}?teamId={TEAM}", headers=H).json()
    if s.get("readyState") in ("READY", "ERROR"):
        break
    time.sleep(3)
print("state", s.get("readyState"))
prj = requests.get(f"{API}/v9/projects/{PROJECT}?teamId={TEAM}", headers=H).json()
if not (prj.get("webAnalytics") or {}).get("enabledAt"):
    print("analytics", requests.post(f"{API}/web/insights/toggle?projectId={prj['id']}&teamId={TEAM}", headers=H, json={"value": True}).json())
print("aliases", (prj.get("targets", {}).get("production") or {}).get("alias"))
