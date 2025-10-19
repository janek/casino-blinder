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


def run_claude_commit_push() -> bool:
    """Run claude CLI to commit and push changes."""
    try:
        log("Invoking Claude to commit and push changes...")

        # Run claude CLI with the commit push command
        result = subprocess.run(
            ["claude", "commit push"],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )

        # Log the output
        if result.stdout:
            log(f"Claude output:\n{result.stdout}")
        if result.stderr:
            log(f"Claude stderr:\n{result.stderr}", "WARN")

        # Check if successful
        if result.returncode == 0:
            log("✅ Commit and push successful", "SUCCESS")
            return True
        else:
            log(f"❌ Commit and push failed with code {result.returncode}", "ERROR")
            return False

    except subprocess.TimeoutExpired:
        log("⏱️  Claude command timed out after 2 minutes", "ERROR")
        return False
    except FileNotFoundError:
        log("❌ 'claude' CLI not found. Is it installed?", "ERROR")
        return False
    except Exception as e:
        log(f"❌ Unexpected error: {e}", "ERROR")
        return False


def main():
    """Main loop that periodically commits and pushes."""
    # Parse interval from command line
    interval = DEFAULT_INTERVAL
    if len(sys.argv) > 1 and sys.argv[1] == "--interval":
        try:
            interval = int(sys.argv[2])
        except (IndexError, ValueError):
            log("Invalid interval argument, using default 300 seconds", "WARN")

    log(f"🚀 Auto-commit script started (interval: {interval}s)")
    log(f"📝 Logging to: {LOG_FILE.absolute()}")
    log("Press Ctrl+C to stop")

    iteration = 0

    try:
        while True:
            iteration += 1
            log(f"--- Iteration {iteration} ---")

            # Check for changes
            has_changes, status = check_git_status()

            if has_changes:
                log(f"Changes detected:\n{status}")
                run_claude_commit_push()
            else:
                log("No changes to commit")

            # Wait for next iteration
            log(f"⏳ Waiting {interval} seconds until next check...")
            time.sleep(interval)

    except KeyboardInterrupt:
        log("\n👋 Auto-commit script stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
