#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from git import Repo
import requests
from openai import OpenAI

# =========================
# Env setup
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
# Git helpers
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
# README generation / update
# =========================
def collect_project_context():
    """Collect project name, env keys, requirements, main scripts for README generation."""
    ctx = {}
    try:
        top = run(["git", "rev-parse", "--show-toplevel"])
        ctx["project_name"] = Path(top).name
    except Exception:
        ctx["project_name"] = Path.cwd().name

    req = Path("requirements.txt")
    ctx["requirements"] = req.read_text().strip() if req.exists() else ""

    env_keys = []
    for p in [Path(".env.example"), Path(".env")]:
        if p.exists():
            for ln in p.read_text().splitlines():
                if ln.strip() and not ln.strip().startswith("#") and "=" in ln:
                    env_keys.append(ln.split("=", 1)[0].strip())
    ctx["env_keys"] = sorted(set(env_keys))

    py_files = [p.name for p in Path(".").glob("*.py") if p.name != "ai_git_assistant.py"]
    ctx["main_scripts"] = py_files
    return ctx

def ask_openai_for_readme(ctx: dict) -> str:
    name = ctx.get("project_name", "Project")
    env_list = "\n".join(f"- `{k}`" for k in ctx.get("env_keys", [])) or "- (none)"
    install_cmd = "pip install -r requirements.txt" if ctx.get("requirements") else "pip install <dependencies>"
    usage_cmd = f"python {ctx['main_scripts'][0]}" if ctx.get("main_scripts") else "python main.py"

    prompt = f"""Write a professional GitHub README.md for a Python project called "{name}".
Include these sections in this order:

# <Title>
One-paragraph description of what the project does.

## Features
Short bullet list of key capabilities.

## Installation
Exact steps to install (use: {install_cmd}).

## Usage
How to run the project (primary command: {usage_cmd}).

## Configuration
Environment variables if needed:
{env_list}

## Development
- How to run locally
- How to run tests (if any)
- Coding style standards

## Features / Changelog
Add a single placeholder bullet here.
"""
    r = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You write excellent, practical READMEs for real projects."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    readme = r.choices[0].message.content.strip()
    if CHANGELOG_HEADER not in readme:
        readme += f"\n\n{CHANGELOG_HEADER}\n- _Initial placeholder_\n"
    return readme

def ask_openai_to_update_readme(current: str, commit_msg: str, diff: str) -> str:
    prompt = f"""Here is the current README.md:

{current}

Here is the new commit message:
{commit_msg}

Here is the git diff:
{diff}

Update the README.md to reflect the new changes.
- Add new features to the Features section if relevant.
- Update Usage or Configuration if needed.
- Do NOT remove existing information.
- Keep all original sections.
- Do NOT wrap the file in code fences.
Return the full updated README.md.
"""
    r = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You update README.md files professionally for software projects."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return r.choices[0].message.content.strip()

def ensure_readme(commit_msg: str, diff: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    summary = commit_msg.splitlines()[0]

    if not README_PATH.exists():
        ctx = collect_project_context()
        readme = ask_openai_for_readme(ctx)
        README_PATH.write_text(readme + "\n", encoding="utf-8")
    else:
        current = README_PATH.read_text(encoding="utf-8")
        updated = ask_openai_to_update_readme(current, commit_msg, diff)
        README_PATH.write_text(updated + "\n", encoding="utf-8")

    # Always append changelog entry
    lines = README_PATH.read_text(encoding="utf-8").splitlines(True)
    output = []
    inserted = False
    for line in lines:
        output.append(line)
        if line.strip() == CHANGELOG_HEADER and not inserted:
            output.append(f"- **{ts}**: {summary}\n")
            inserted = True
    if not inserted:
        if output and not output[-1].endswith("\n"):
            output[-1] += "\n"
        output.append("\n" + CHANGELOG_HEADER + "\n")
        output.append(f"- **{ts}**: {summary}\n")

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
        "OPENAI_API_KEY=your-openai-api-key\n"
        "SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz\n"
        "MODEL=gpt-4o-mini\n",
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

    ensure_readme(commit_msg, diff)

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
