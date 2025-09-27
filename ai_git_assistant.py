#!/usr/bin/env python3
import os
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from git import Repo
import requests
from openai import OpenAI

# =========================
# Env + client setup
# =========================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SLACK_WEBHOOK_URL = (os.getenv("SLACK_WEBHOOK_URL") or "").strip()
MODEL = (os.getenv("MODEL") or "gpt-4o-mini").strip()

if not OPENAI_API_KEY:
    print("❌ Missing OPENAI_API_KEY in .env")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

README_PATH = Path("README.md")
CHANGELOG_HEADER = "## Features / Changelog"

# =========================
# Basic helpers
# =========================
def run(cmd):
    return subprocess.check_output(cmd, text=True).strip()

def get_diff():
    try:
        return run(["git", "diff", "--staged", "-U0"])
    except subprocess.CalledProcessError:
        return ""

def clean_commit_message(raw: str) -> str:
    lines = [l.rstrip() for l in raw.splitlines()]
    out = []
    for l in lines:
        s = l.strip()
        if not s:
            if out and out[-1] != "":
                out.append("")
            continue
        if s.startswith("```"):
            continue
        out.append(s)
    # collapse multiple blanks
    cleaned = []
    for l in out:
        if l == "" and (not cleaned or cleaned[-1] == ""):
            continue
        cleaned.append(l)
    return "\n".join(cleaned).strip()

def ask_openai_for_commit(diff: str) -> str:
    prompt = f"""You are an expert developer.
Here is a git diff of staged changes:

{diff}

Write a Conventional Commit message:
- One of: feat:, fix:, docs:, refactor:, test:, chore:, perf:
- Summary line <= 72 chars
- Optional short body with bullet points
- Do NOT include markdown code fences or backticks
- Do NOT wrap the message in quotes
"""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You write excellent, concise conventional commits."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return clean_commit_message(resp.choices[0].message.content)

# =========================
# README: detection & cleanup
# =========================
LEGACY_BULLET_RE = re.compile(r"^\s*-\s*\d{4}-\d{2}-\d{2}.*`{3}\s*$")

def looks_legacy_or_broken(text: str) -> bool:
    # Legacy bullets at top or missing changelog header
    first_nonblank = next((ln for ln in text.splitlines() if ln.strip()), "")
    if LEGACY_BULLET_RE.match(first_nonblank):
        return True
    if CHANGELOG_HEADER not in text:
        return True
    return False

def cleanup_legacy_lines(text: str) -> str:
    """Remove any leading legacy bullet lines like '- 2025-09-27 … ```' before first header."""
    lines = text.splitlines()
    i = 0
    while i < len(lines) and (not lines[i].strip() or LEGACY_BULLET_RE.match(lines[i])):
        i += 1
    return "\n".join(lines[i:]).strip() + "\n"

# =========================
# README: OpenAI generation
# =========================
def collect_project_context() -> dict:
    ctx = {}
    # repo name
    try:
        top = run(["git", "rev-parse", "--show-toplevel"])
        ctx["project_name"] = Path(top).name
    except Exception:
        ctx["project_name"] = Path.cwd().name

    # dependencies
    req = Path("requirements.txt")
    ctx["requirements"] = req.read_text().strip() if req.exists() else ""

    # env keys (from .env.example or .env)
    env_keys = []
    for p in [Path(".env.example"), Path(".env")]:
        if p.exists():
            for ln in p.read_text().splitlines():
                if ln.strip() and not ln.strip().startswith("#") and "=" in ln:
                    env_keys.append(ln.split("=", 1)[0].strip())
    ctx["env_keys"] = sorted(set(env_keys))

    # primary script info
    main_script = Path("ai_git_assistant.py")
    ctx["has_ai_assistant"] = main_script.exists()
    return ctx

def ask_openai_for_readme(ctx: dict) -> str:
    name = ctx.get("project_name", "Project")
    env_list = "\n".join(f"- `{k}`" for k in ctx.get("env_keys", [])) or "- (none)"
    req_present = bool(ctx.get("requirements"))
    usage_block = "python ai_git_assistant.py" if ctx.get("has_ai_assistant") else "python main.py"

    prompt = f"""Write a professional GitHub README.md in clean Markdown for a Python repo named "{name}".
Include ONLY these sections in this order:

# <Title>
One-paragraph description (what it does and why).

## Features
Short bullets of key capabilities.

## Installation
Exact commands to set up (assume Python + pip). If requirements.txt exists, show 'pip install -r requirements.txt'.

## Usage
Show the primary command a user runs (use: {usage_block}). Explain any flags briefly.

## Configuration
List environment variables discovered in the repo:
{env_list}

## Development
- How to run locally
- How to run tests (if any)
- Coding standards (brief)

## Features / Changelog
Add a single bullet placeholder line. Do NOT include code fences around the entire file. Keep formatting tight and readable.
"""
    r = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You write excellent, practical READMEs for engineering teams."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    readme = r.choices[0].message.content.strip()

    # Ensure the required header exists
    if CHANGELOG_HEADER not in readme:
        readme += f"\n\n{CHANGELOG_HEADER}\n- _Initial placeholder_\n"
    return readme

def ensure_readme(commit_summary: str):
    """
    If README is missing or legacy/broken: generate a new one with OpenAI.
    Else: clean legacy top bullets if present, keep existing content.
    Then append a new changelog line.
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    if not README_PATH.exists():
        ctx = collect_project_context()
        readme = ask_openai_for_readme(ctx)
        with open(README_PATH, "w") as f:
            f.write(readme.strip() + "\n")
    else:
        current = README_PATH.read_text(encoding="utf-8")
        if looks_legacy_or_broken(current):
            ctx = collect_project_context()
            readme = ask_openai_for_readme(ctx)
            # preserve nothing—replace with clean AI README
            with open(README_PATH, "w", encoding="utf-8") as f:
                f.write(readme.strip() + "\n")
        else:
            # Clean legacy leading bullets if any (safe idempotent)
            cleaned = cleanup_legacy_lines(current)
            with open(README_PATH, "w", encoding="utf-8") as f:
                f.write(cleaned)

    # Append changelog entry
    lines = README_PATH.read_text(encoding="utf-8").splitlines(True)
    output = []
    inserted = False
    for line in lines:
        output.append(line)
        if line.strip() == CHANGELOG_HEADER and not inserted:
            output.append(f"- **{ts}**: {commit_summary}\n")
            inserted = True
    if not inserted:
        if output and not output[-1].endswith("\n"):
            output[-1] = output[-1] + "\n"
        output.append("\n" + CHANGELOG_HEADER + "\n")
        output.append(f"- **{ts}**: {commit_summary}\n")

    README_PATH.write_text("".join(output), encoding="utf-8")

# =========================
# Slack
# =========================
def slack_notify(commit_msg: str):
    if not SLACK_WEBHOOK_URL:
        return
    payload = {"text": f"AI Commit:\n{commit_msg}"}
    try:
        requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=8)
    except Exception:
        pass

# =========================
# Main
# =========================
def ensure_env_example():
    p = Path(".env.example")
    if p.exists():
        return
    p.write_text(
        "# Example .env for AI Git Assistant\n\n"
        "# Required\nOPENAI_API_KEY=your-openai-api-key\n\n"
        "# Optional\nSLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz\nMODEL=gpt-4o-mini\n",
        encoding="utf-8",
    )

def main():
    repo = Repo(".")
    diff = get_diff()
    if not diff:
        print("No staged changes found. Run `git add` first.")
        sys.exit(1)

    commit_msg = ask_openai_for_commit(diff)
    print("\n=== Generated Commit Message ===\n" + commit_msg + "\n")

    # README generation/cleanup + changelog append
    summary = commit_msg.splitlines()[0]
    ensure_readme(summary)

    # Commit + push
    repo.git.add("README.md")
    repo.index.commit(commit_msg)
    try:
        current_branch = repo.active_branch.name
        repo.git.push("origin", current_branch)
        print(f"✅ Pushed to {current_branch}.")
    except Exception as e:
        print(f"⚠️ Push failed: {e}")

    slack_notify(commit_msg)
    ensure_env_example()
    print("✅ Done.")

if __name__ == "__main__":
    main()
