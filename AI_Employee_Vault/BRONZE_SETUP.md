# AI Employee - Bronze Tier Setup

> **Personal AI Employee Hackathon 0**  
> **Tier**: Bronze (Foundation)  
> **Estimated Setup Time**: 30 minutes

This guide walks you through setting up the Bronze Tier of your Personal AI Employee.

---

## 📋 Bronze Tier Deliverables

- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] One working Watcher script (File System monitoring)
- [x] Qwen Code integration for reading/writing to vault
- [x] Basic folder structure: /Inbox, /Needs_Action, /Done
- [x] Ralph Wiggum persistence plugin

---

## 🚀 Quick Start

### Step 1: Install Prerequisites

```bash
# Install Qwen Code
npm install -g @anthropic/Qwen-code

# Verify installation
qwen --version

# Install Python dependencies for watchers
pip install watchdog
```

### Step 2: Verify Vault Structure

Your vault should have this structure:

```
AI_Employee_Vault/
├── Dashboard.md           # Main dashboard
├── Company_Handbook.md    # Rules of engagement
├── Business_Goals.md      # Objectives and metrics
├── Inbox/                 # Drop folder for files
├── Needs_Action/          # Items requiring attention
├── Plans/                 # Generated plans
├── Pending_Approval/      # Awaiting human approval
├── Approved/              # Approved actions
├── Done/                  # Completed items
├── Logs/                  # Activity logs
└── scripts/               # Python scripts
    ├── base_watcher.py
    ├── filesystem_watcher.py
    └── orchestrator.py
```

### Step 3: Test File System Watcher

The File System Watcher monitors the `Inbox/` folder for new files.

```bash
# Navigate to vault
cd AI_Employee_Vault

# Start the watcher (Terminal 1)
python scripts/filesystem_watcher.py .

# In another terminal, drop a test file:
echo "Test content" > Inbox/test_document.txt

# Watch the watcher create an action file in Needs_Action/
```

Expected output:
```
2026-02-25 10:30:00 - FileSystemWatcher - INFO - Found 1 new file(s) in drop folder
2026-02-25 10:30:00 - FileSystemWatcher - INFO - Copied file to: Needs_Action/test_document.txt
2026-02-25 10:30:00 - FileSystemWatcher - INFO - Created metadata file: test_document.md
```

### Step 4: Test Orchestrator

The Orchestrator triggers Qwen Code to process items in Needs_Action.

```bash
# Start orchestrator in dry-run mode first (Terminal 2)
python scripts/orchestrator.py . --dry-run --interval 10

# You should see:
# [DRY RUN] Would trigger Qwen with prompt: ...
```

### Step 5: Full Integration Test

```bash
# 1. Start the File System Watcher (background)
python scripts/filesystem_watcher.py . &

# 2. Drop a test file
echo "Please process this document" > Inbox/bronze_test.txt

# 3. Wait for watcher to process (30 seconds)

# 4. Check Needs_Action folder
ls Needs_Action/

# You should see:
# - bronze_test.txt
# - bronze_test.md (metadata file)
```

---

## 📖 Usage Guide

### How the System Works

1. **File Drop**: User drops a file into `Inbox/`
2. **Watcher Detects**: FileSystemWatcher creates action files in `Needs_Action/`
3. **Orchestrator Triggers**: Orchestrator calls Qwen Code to process items
4. **Qwen Acts**: Qwen reads Company_Handbook.md and processes items
5. **Human Approval**: If needed, Qwen creates approval files
6. **Completion**: Processed items moved to `Done/`

### Starting Components

```bash
# Start File System Watcher
python scripts/filesystem_watcher.py .

# Start Orchestrator (in separate terminal)
python scripts/orchestrator.py .

# Or start both with the helper script
bash start.sh
```

### Stopping Components

```bash
# Press Ctrl+C in each terminal
# Or use the stop script
bash stop.sh
```

---

## 🔧 Configuration

### Watcher Settings

Edit `scripts/filesystem_watcher.py` to customize:

```python
# Check interval (default: 30 seconds)
check_interval = 30

# Drop folder (default: vault/Inbox)
drop_folder = vault_path / 'Inbox'
```

### Orchestrator Settings

Edit `scripts/orchestrator.py` to customize:

```python
# Orchestration interval (default: 60 seconds)
check_interval = 60

# Dry run mode (default: False)
dry_run = False
```

### Ralph Wiggum Settings

Edit `.Qwen/ralph_config.yaml`:

```yaml
max_iterations: 10  # Maximum loop iterations
check_interval: 5   # Seconds between checks
```

---

## 🧪 Testing Checklist

### Bronze Tier Completion Checklist

- [ ] Vault folders exist (Inbox, Needs_Action, Done, etc.)
- [ ] Dashboard.md displays correctly in Obsidian
- [ ] Company_Handbook.md is readable
- [ ] Business_Goals.md is configured
- [ ] FileSystemWatcher starts without errors
- [ ] Dropping a file in Inbox creates action file in Needs_Action
- [ ] Orchestrator runs without errors
- [ ] Qwen Code can read and write to vault
- [ ] Ralph Wiggum plugin is installed

### Test Commands

```bash
# Test 1: Verify folder structure
ls -la

# Test 2: Start watcher (dry run)
python scripts/filesystem_watcher.py . --interval 5

# Test 3: Drop test file
echo "Test" > Inbox/test.txt

# Test 4: Check Needs_Action
ls Needs_Action/

# Test 5: Verify Qwen Code
qwen --version

# Test 6: Test Qwen with vault
Qwen --prompt "Read Dashboard.md and summarize"
```

---

## 🐛 Troubleshooting

### Watcher Not Detecting Files

**Problem**: Files dropped in Inbox are not processed.

**Solutions**:
1. Check file permissions: `ls -la Inbox/`
2. Verify watcher is running: `ps aux | grep filesystem_watcher`
3. Check logs: `cat Logs/*.log`
4. Try shorter interval: `python scripts/filesystem_watcher.py . --interval 5`

### Qwen Code Not Found

**Problem**: `Qwen: command not found`

**Solutions**:
1. Install Qwen Code: `npm install -g @anthropic/Qwen-code`
2. Verify PATH: `echo $PATH`
3. Restart terminal
4. Use full path: `C:\Users\YourName\AppData\Roaming\npm\Qwen`

### Orchestrator Fails to Trigger Qwen

**Problem**: Orchestrator runs but Qwen doesn't process items.

**Solutions**:
1. Check Qwen is authenticated: `qwen --version`
2. Run orchestrator in dry-run first: `--dry-run`
3. Check logs: `cat Logs/orchestrator.log`
4. Verify vault path is correct

### Ralph Wiggum Not Working

**Problem**: Qwen exits after one iteration.

**Solutions**:
1. Verify plugin is in `.Qwen/plugins/`
2. Check config: `cat .Qwen/ralph_config.yaml`
3. Use `/ralph-loop` command in Qwen
4. Check state folder: `ls .Qwen/state/`

---

## 📝 Next Steps (Silver Tier)

After completing Bronze tier, consider adding:

1. **Gmail Watcher**: Monitor Gmail for important emails
2. **WhatsApp Watcher**: Monitor WhatsApp for urgent messages
3. **MCP Server**: Integrate email sending capability
4. **Approval Workflow**: Human-in-the-loop for sensitive actions
5. **Scheduled Briefings**: Generate weekly CEO briefings

---

## 📚 Resources

- [Qwen Code Documentation](https://Qwen.com/product/Qwen-code)
- [Obsidian Download](https://obsidian.md/download)
- [Agent Skills Documentation](https://platform.Qwen.com/docs/en/agents-and-tools/agent-skills/overview)
- [Watchdog Package](https://pypi.org/project/watchdog/)

---

## 🆘 Getting Help

- Check the logs in `Logs/` folder
- Review `Company_Handbook.md` for rules
- Join Wednesday Research Meetings (10:00 PM PKT)
- YouTube: https://www.youtube.com/@panaversity

---

*Bronze Tier Setup Complete!* 🎉

*Now your AI Employee can monitor files and trigger Qwen Code for processing.*

