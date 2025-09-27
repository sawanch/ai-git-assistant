#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime

from dotenv import load_dotenv
from git import Repo
import requests
from openai import OpenAI

# -----------------------------
# Env + client setup
# -----------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "").strip()
MODEL = os.getenv("MODEL", "gpt-4o-mini").strip()  # default

if not OPENAI_API_KEY:
    print(" Missing OPENAI_API_KEY in .env")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

# -----------------------------
# Helpers
# -----------------------------
def run(cmd):
    """Run a shell command and return stdout as text."""
    return subprocess.check_output(cmd, text=True).strip()

def get_diff():
    """Return staged diff (unified=0 for concise). Empty string if none."""
    try:
        return run(["git", "diff", "--staged", "-U0"])
    except subprocess.CalledProcessError:
        return ""

def clean_commit_message(raw_msg: str) -> str:
    """
    Remove code fences and blank noise lines from AI output.
    Keep meaningful lines only.
    """
    lines = [l.rstrip() for l in raw_msg.splitlines()]
    cleaned = []
    for l in lines:
        s = l.strip()
        if not s:
            # allow single blank line between summary and body
            if cleaned and cleaned[-1] != "":
                cleaned.append("")
            continue
        if s.startswith("```"):
            continue
        cleaned.append(l.strip())
    # collapse multiple blanks
    final = []
    for l in cleaned:
        if l == "" and (not final or final[-1] == ""):
            continue
        final.append(l)
    return "\n".join(final).strip()

def ask_openai(diff: str) -> str:
    """
    Ask the model for a Conventional Commit message from the staged diff.
    """
    prompt = f"""You are an expert developer.
Here is a git diff of staged changes:

{diff}

Write a clear Conventional Commit message:
- Use one of: feat:, fix:, docs:, refactor:, test:, chore:, perf:
- Keep the summary line <= 72 chars
- Optionally include a short body with bullet points
- DO NOT include markdown code fences or backticks
- DO NOT include quotes around the message
"""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You write excellent, concise conventional commit messages."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return clean_commit_message(resp.choices[0].message.content)

# -----------------------------
# README handling
# -----------------------------
README_PATH = "README.md"
CHANGELOG_HEADER = "## Features / Changelog"

README_TEMPLATE = """# AI Git Assistant

AI Git Assistant automatically generates clean Conventional Commit messages using AI,
updates this README with feature changes, and (optionally) notifies a Slack channel.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
# stage your changes first
git add <files>
python ai_git_assistant.py
```

## Configuration
Create a `.env` file with:
- `OPENAI_API_KEY`
- `SLACK_WEBHOOK_URL` (optional)
- `MODEL` (optional, default: gpt-4o-mini)

{changelog}
- **{ts}**: {summary}
"""

def ensure_env_example():
    """Create .env.example if it does not exist."""
    path = ".env.example"
    if os.path.exists(path):
        return
    example = """# Example .env for AI Git Assistant

# Required
OPENAI_API_KEY=your-openai-api-key

# Optional
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz
MODEL=gpt-4o-mini
"""
    with open(path, "w") as f:
        f.write(example)

def update_readme_with_entry(summary: str):
    """
    Ensure README exists with an industry-style template.
    Then add a new bullet under '## Features / Changelog'.
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    if not os.path.exists(README_PATH):
        with open(README_PATH, "w") as f:
            f.write(
                README_TEMPLATE.format(
                    changelog=CHANGELOG_HEADER,
                    ts=ts,
                    summary=summary
                )
            )
        return

    # Append the new line under the changelog header, creating the header if missing.
    with open(README_PATH, "r") as f:
        lines = f.readlines()

    new_lines = []
    inserted = False
    found_header = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        new_lines.append(line)

        if stripped == CHANGELOG_HEADER and not inserted:
            found_header = True
            # Immediately insert the new entry after the header line
            new_lines.append(f"- **{ts}**: {summary}\n")
            inserted = True

    if not found_header:
        # Add a new section at the end
        if new_lines and new_lines[-1] and not new_lines[-1].endswith("\n"):
            new_lines[-1] += "\n"
        new_lines.append("\n" + CHANGELOG_HEADER + "\n")
        new_lines.append(f"- **{ts}**: {summary}\n")
        inserted = True

    with open(README_PATH, "w") as f:
        f.writelines(new_lines)

# -----------------------------
# Slack
# -----------------------------
def slack_notify(commit_msg: str):
    if not SLACK_WEBHOOK_URL:
        return
    payload = {"text": f"AI Commit:\n{commit_msg}"}
    try:
        requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=8)
    except Exception:
        pass  # avoid failing the whole flow on Slack issues

# -----------------------------
# Main
# -----------------------------
def main():
    repo = Repo(".")
    diff = get_diff()
    if not diff:
        print("No staged changes found. Run `git add` first.")
        sys.exit(1)

    commit_msg = ask_openai(diff)
    print("\n=== Generated Commit Message ===\n" + commit_msg + "\n")

    # Update README (industry template + append to changelog)
    summary = commit_msg.splitlines()[0]
    update_readme_with_entry(summary)

    # Commit & push
    repo.git.add(README_PATH)
    repo.index.commit(commit_msg)
    try:
        # use current branch instead of assuming "main"
        current_branch = repo.active_branch.name
        repo.git.push("origin", current_branch)
        print(f"✅ Changes pushed to GitHub (branch: {current_branch}).")
    except Exception as e:
        print(f"⚠️ Push failed: {e}")

    slack_notify(commit_msg)
    print("✅ Slack notified (if configured).")

    ensure_env_example()

if __name__ == "__main__":
    main()
