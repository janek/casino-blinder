# Auto-Commit Script - System-Wide Setup Guide

This guide explains how to install the `auto_commit.py` script system-wide so you can use it in **any repository**.

---

## What Does This Script Do?

The auto-commit script:
- 🔄 Runs in a continuous loop (default: every 5 minutes)
- 🔍 Checks for uncommitted changes in your git repo
- 🤖 Uses the `claude` CLI to generate commit messages and push changes
- 📝 Logs all activity to `tools/auto_commit.log`
- ⏹️  Stops gracefully with Ctrl+C

---

## Prerequisites

1. **Claude Code CLI** must be installed and authenticated
   ```bash
   # Check if installed
   which claude

   # If not installed, follow: https://docs.claude.com/en/docs/claude-code/installation
   ```

2. **uv** (Python package manager) must be installed
   ```bash
   # Check if installed
   which uv

   # If not installed: https://docs.astral.sh/uv/getting-started/installation/
   ```

3. **Git repository** - run this in a repo with remote configured

---

## Installation Options

### Option 1: Add to PATH (Recommended)

This makes the script available as a simple `auto-commit` command from anywhere.

#### Step 1: Create bin directory
```bash
mkdir -p ~/.local/bin
```

#### Step 2: Copy script
```bash
cp tools/auto_commit.py ~/.local/bin/auto-commit
chmod +x ~/.local/bin/auto-commit
```

#### Step 3: Ensure ~/.local/bin is in PATH

Add this to your shell config file (`~/.zshrc` for Zsh or `~/.bash_profile` for Bash):

```bash
# Add to ~/.zshrc or ~/.bash_profile
export PATH="$HOME/.local/bin:$PATH"
```

#### Step 4: Reload shell
```bash
# For Zsh (macOS default)
source ~/.zshrc

# For Bash
source ~/.bash_profile
```

#### Step 5: Verify installation
```bash
which auto-commit
# Should output: /Users/[your-username]/.local/bin/auto-commit
```

---

### Option 2: Global uv Script Directory

Alternative approach using a dedicated scripts directory.

#### Step 1: Create scripts directory
```bash
mkdir -p ~/.config/uv-scripts
```

#### Step 2: Copy script
```bash
cp tools/auto_commit.py ~/.config/uv-scripts/auto_commit.py
```

#### Step 3: Create alias

Add to `~/.zshrc` or `~/.bash_profile`:

```bash
alias auto-commit='uv run ~/.config/uv-scripts/auto_commit.py'
```

#### Step 4: Reload shell
```bash
source ~/.zshrc  # or source ~/.bash_profile
```

---

### Option 3: Symlink from Repo (Development)

Keep the script in this repo and symlink to it.

```bash
ln -s /Users/janek/Developer/personal/casino-blinder/tools/auto_commit.py ~/.local/bin/auto-commit
```

**Pros:** Edit in one place, changes immediately available
**Cons:** Breaks if you move/delete the repo

---

## Usage

Once installed, navigate to **any git repository** and run:

```bash
# Default: check every 5 minutes (300 seconds)
auto-commit

# Custom interval: check every 3 minutes (180 seconds)
auto-commit --interval 180

# Custom interval: check every 10 minutes
auto-commit --interval 600
```

### Running in Background

To run the script in the background (survives terminal close):

```bash
# Using nohup (traditional Unix)
nohup auto-commit > /dev/null 2>&1 &

# Or using macOS background job
auto-commit &
disown

# To stop, find the process and kill it
ps aux | grep auto_commit
kill [PID]
```

### Viewing Logs

The script logs to `tools/auto_commit.log` in the repository:

```bash
# Watch live
tail -f tools/auto_commit.log

# View recent entries
tail -n 50 tools/auto_commit.log

# Search for errors
grep ERROR tools/auto_commit.log
```

---

## Configuration

### Changing the Default Interval

Edit the script and change:
```python
DEFAULT_INTERVAL = 300  # Change to desired seconds
```

### Changing Log Location

Edit the script and change:
```python
LOG_FILE = Path("tools/auto_commit.log")  # Change to desired path
```

For system-wide installation, consider using:
```python
LOG_FILE = Path.home() / ".auto_commit.log"  # Logs to ~/.auto_commit.log
```

### Customizing Claude Prompt

To change what prompt is sent to Claude, edit the `run_claude_commit_push()` function:

```python
result = subprocess.run(
    ["claude", "commit push"],  # Change this command
    ...
)
```

Examples:
- `["claude", "commit with detailed message and push"]`
- `["claude", "review changes, commit, and push"]`

---

## Troubleshooting

### "claude: command not found"

The Claude Code CLI isn't installed or not in PATH.

**Fix:**
```bash
# Check PATH
echo $PATH

# Try finding claude
which claude

# If not found, reinstall Claude Code CLI
```

### Script doesn't detect changes

Make sure you're in a git repository:

```bash
# Check if in git repo
git status

# If not, initialize
git init
```

### Permission denied

Make the script executable:

```bash
chmod +x ~/.local/bin/auto-commit
```

### Claude takes too long / times out

The script has a 2-minute timeout for Claude commands. If it's timing out:

1. Check network connection
2. Check Claude API status
3. Increase timeout in script:
   ```python
   timeout=300  # 5 minutes
   ```

---

## Uninstallation

### Remove from PATH
```bash
rm ~/.local/bin/auto-commit
```

### Remove alias method
Remove the `alias auto-commit=...` line from `~/.zshrc` or `~/.bash_profile`, then:
```bash
source ~/.zshrc  # or source ~/.bash_profile
```

### Remove script directory
```bash
rm -rf ~/.config/uv-scripts
```

---

## Advanced Usage

### Use with launchd (macOS Auto-Start)

Create `~/Library/LaunchAgents/com.user.auto-commit.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.auto-commit</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/janek/.local/bin/auto-commit</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/janek/Developer/personal/casino-blinder</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/auto-commit.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/auto-commit.err</string>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.user.auto-commit.plist
```

Unload it:
```bash
launchctl unload ~/Library/LaunchAgents/com.user.auto-commit.plist
```

---

## Best Practices

✅ **DO:**
- Run in development/personal projects where auto-commits make sense
- Monitor the log file periodically
- Test in a branch first before running on main
- Set a reasonable interval (5-15 minutes is good)

❌ **DON'T:**
- Run on production codebases without supervision
- Run with very short intervals (<1 minute) - you'll spam commits
- Forget it's running - stop it when you're done working
- Use in shared repos without team agreement

---

## FAQ

**Q: Will this commit incomplete work?**
A: Yes, it commits whatever changes exist. Use git stash if you have WIP code you don't want committed.

**Q: Can I customize commit messages?**
A: The messages are generated by Claude. You can modify the prompt sent to the `claude` CLI in the script.

**Q: Does this work on Linux/Windows?**
A: Linux: Yes (same setup). Windows: Needs adaptation (use Task Scheduler instead of launchd).

**Q: What happens if Claude is down?**
A: The script logs an error and waits until the next interval to try again.

**Q: Can I run multiple instances in different repos?**
A: Yes! Each instance runs independently in its own working directory.

---

## See Also

- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Git Best Practices](https://git-scm.com/book/en/v2)

---

**Questions or Issues?**
Check the log file at `tools/auto_commit.log` for detailed error messages.
