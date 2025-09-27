#!/usr/bin/env python3
import os, subprocess, sys
from datetime import datetime
from dotenv import load_dotenv
from git import Repo
import requests
from openai import OpenAI

# --- Load secrets ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
MODEL = os.getenv("MODEL", "gpt-4o-mini")

client = OpenAI(api_key=OPENAI_API_KEY)

# --- Helpers ---
def run(cmd):
    return subprocess.check_output(cmd, text=True).strip()

def get_diff():
    try:
        return run(["git", "diff", "--staged", "-U0"])
    except subprocess.CalledProcessError:
        return ""

def ask_openai(diff):
    prompt = f"""You are an expert developer.
Here is a git diff of staged changes:

{diff}

Write a clear Conventional Commit message (e.g., feat: ..., fix: ..., docs: ...).
Keep summary <= 72 chars. If needed, add a short body."""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You write excellent git commit messages."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return resp.choices[0].message.content.strip()

def update_readme(commit_msg):
    readme = "README.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    first_line = commit_msg.splitlines()[0].replace("`", "")
    entry = f"- {timestamp}: {first_line}\n"
    if os.path.exists(readme):
        with open(readme, "a") as f:
            f.write(entry)
    else:
        with open(readme, "w") as f:
            f.write("# Project Log\n\n" + entry)

def slack_notify(commit_msg):
    if not SLACK_WEBHOOK_URL: return
    payload = {"text": f"AI Commit: {commit_msg}"}
    requests.post(SLACK_WEBHOOK_URL, json=payload)

def main():
    repo = Repo(".")
    diff = get_diff()
    if not diff:
        print("No staged changes found. Run `git add` first.")
        sys.exit(1)

    commit_msg = ask_openai(diff)
    print("\n=== Generated Commit Message ===")
    print(commit_msg)

    update_readme(commit_msg)

    repo.git.add("README.md")
    repo.index.commit(commit_msg)
    try:
        repo.git.push("origin", "main")
        print("Changes pushed to GitHub.")
    except Exception as e:
        print(f"Push failed: {e}")

    slack_notify(commit_msg)
    print("Slack notified.")

if __name__ == "__main__":
    main()
