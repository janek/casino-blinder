#!/usr/bin/env python3
"""
Auto-commit script that periodically asks Claude to commit and push changes.

Usage:
    uv run tools/auto_commit.py [--interval SECONDS]

This script runs in a loop, checking for changes and using Claude Code CLI
to commit and push them automatically.
"""

import subprocess
import time
import sys
from datetime import datetime
from pathlib import Path

# Configuration
DEFAULT_INTERVAL = 300  # 5 minutes in seconds
LOG_FILE = Path("tools/auto_commit.log")


def log(message: str, level: str = "INFO"):
    """Log a message to both stdout and log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"

    print(log_entry)

    # Append to log file
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")


def check_git_status() -> tuple[bool, str]:
    """Check if there are uncommitted changes."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        has_changes = bool(result.stdout.strip())
        return has_changes, result.stdout
    except subprocess.CalledProcessError as e:
        log(f"Error checking git status: {e}", "ERROR")
        return False, ""


def get_recent_commits(count: int = 5) -> str:
    """Get recent commit messages."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{count}", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return ""


def extract_important_notes(text: str) -> list[str]:
    """Extract important notes from Claude's output (gitignore suggestions, warnings, etc.)."""
    notes = []
    lines = text.split('\n')

    # Look for lines with important keywords
    for line in lines:
        line = line.strip()
        if any(keyword in line.lower() for keyword in ['gitignore', 'note:', 'warning:', 'important:']):
            # Skip markdown symbols and clean up
            line = line.lstrip('#*-').strip()
            if line:
                notes.append(line)

    return notes


def run_claude_commit_push() -> bool:
    """Run claude CLI to commit and push changes."""
    try:
        # Capture commit hash before running Claude
        before_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        before_hash = before_result.stdout.strip()

        # Run claude CLI with the commit push command (suppress verbose output)
        result = subprocess.run(
            ["claude", "commit push"],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )

        # Check if successful
        if result.returncode == 0:
            # Get new commit messages
            after_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            after_hash = after_result.stdout.strip()

            # If commits were made, show them
            if before_hash != after_hash:
                commits = get_recent_commits(5)
                if commits:
                    print(commits)

            # Extract and show any important notes
            notes = extract_important_notes(result.stdout)
            if notes:
                print("\n" + "\n".join(notes))

            return True
        else:
            log(f"Commit failed (code {result.returncode})", "ERROR")
            if result.stderr:
                print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        log("Timed out after 2 minutes", "ERROR")
        return False
    except FileNotFoundError:
        log("'claude' CLI not found", "ERROR")
        return False
    except Exception as e:
        log(f"Error: {e}", "ERROR")
        return False


def main():
    """Main loop that periodically commits and pushes."""
    # Parse interval from command line
    interval = DEFAULT_INTERVAL
    if len(sys.argv) > 1 and sys.argv[1] == "--interval":
        try:
            interval = int(sys.argv[2])
        except (IndexError, ValueError):
            print("Invalid interval, using default 300s")

    print(f"Started (checking every {interval}s, Ctrl+C to stop)")

    try:
        while True:
            # Check for changes
            has_changes, _ = check_git_status()

            if has_changes:
                run_claude_commit_push()

            # Wait for next iteration
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nStopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
