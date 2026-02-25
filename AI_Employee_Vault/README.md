# AI Employee - Bronze Tier

> **Personal AI Employee Hackathon 0**
> **Foundation Layer - Minimum Viable Deliverable**

A local-first, autonomous AI employee that monitors files and triggers Qwen Code for intelligent processing.

---

## 🎯 Bronze Tier Features

- ✅ **Obsidian Vault** with Dashboard, Company Handbook, and Business Goals
- ✅ **File System Watcher** - Monitors Inbox folder for new files
- ✅ **Orchestrator** - Triggers Qwen Code to process pending items
- ✅ **Ralph Wiggum Plugin** - Keeps Qwen working until tasks complete
- ✅ **Folder Structure** - Inbox, Needs_Action, Done, Plans, Approval workflows

---

## 📁 Project Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time status dashboard
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Objectives and metrics
├── BRONZE_SETUP.md           # Detailed setup guide
├── start.bat                 # Start all services (Windows)
├── stop.bat                  # Stop all services (Windows)
│
├── Inbox/                    # Drop files here for processing
├── Needs_Action/             # Items requiring attention
├── Plans/                    # Generated action plans
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Approved actions ready to execute
├── Done/                     # Completed items archive
├── Logs/                     # Activity logs
│
├── scripts/
│   ├── base_watcher.py       # Abstract base class for watchers
│   ├── filesystem_watcher.py # File system monitoring script
│   ├── orchestrator.py       # Master orchestration script
│   └── requirements.txt      # Python dependencies
│
└── .qwen/
    ├── plugins/
    │   └── ralph_wiggum.py   # Persistence plugin
    └── ralph_config.yaml     # Ralph configuration
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r scripts/requirements.txt

# Verify Qwen Code is installed
qwen --version
```

### 2. Start the AI Employee

```bash
# Windows
start.bat .

# Or manually start components:
python scripts/filesystem_watcher.py .
python scripts/orchestrator.py .
```

### 3. Test It

```bash
# Drop a test file in the Inbox
echo "Please process this document" > Inbox/test.txt

# Watch the magic happen:
# 1. FileSystemWatcher detects the file
# 2. Creates action file in Needs_Action/
# 3. Orchestrator triggers Qwen Code
# 4. Qwen processes the item
# 5. Result moved to Done/
```

---

## 📖 How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    EXTERNAL TRIGGER                     │
│                    (File Drop in Inbox)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              PERCEPTION LAYER                           │
│           FileSystemWatcher (Python)                    │
│   - Monitors Inbox/ every 30 seconds                    │
│   - Creates action files in Needs_Action/               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              OBSIDIAN VAULT                             │
│   /Needs_Action/                                        │
│   - test_file.md (metadata + content)                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              ORCHESTRATION LAYER                        │
│           Orchestrator (Python)                         │
│   - Checks Needs_Action/ every 60 seconds               │
│   - Triggers Qwen Code with context                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              REASONING LAYER                            │
│              Qwen Code                                │
│   - Reads Company_Handbook.md for rules                 │
│   - Processes items per guidelines                      │
│   - Creates plans, requests approvals                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              ACTION LAYER                               │
│   - Move files to Done/                                 │
│   - Update Dashboard.md                                 │
│   - Log actions to Logs/                                │
└─────────────────────────────────────────────────────────┘
```

### Component Details

#### FileSystemWatcher

Monitors the `Inbox/` folder for new files:

```bash
python scripts/filesystem_watcher.py . --interval 30
```

**What it does:**
- Scans Inbox/ every 30 seconds
- Copies new files to Needs_Action/
- Creates metadata .md files with context
- Removes processed files from Inbox/

#### Orchestrator

Triggers Qwen Code to process pending items:

```bash
python scripts/orchestrator.py . --interval 60
```

**What it does:**
- Checks Needs_Action/ for pending items
- Creates intelligent prompts for Qwen
- Triggers Qwen Code with context
- Updates Dashboard.md with stats
- Processes approved items

#### Ralph Wiggum Plugin

Keeps Qwen working until tasks are complete:

```bash
python .qwen/plugins/ralph_wiggum.py . "Process all files"
```

**What it does:**
- Tracks iteration count
- Checks if task is complete
- Re-injects prompt if work remains
- Prevents premature exit

---

## ⚙️ Configuration

### Watcher Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `--interval` | 30s | Check interval in seconds |
| `--drop-folder` | Inbox/ | Folder to monitor |

### Orchestrator Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `--interval` | 60s | Orchestration cycle interval |
| `--dry-run` | False | Log without executing |

---

## 🧪 Testing

### Verify Installation

```bash
# Check Python version
python --version  # Should be 3.13+

# Check dependencies
pip list | grep watchdog

# Check Qwen Code
qwen --version

# Test watcher (dry run)
python scripts/filesystem_watcher.py . --interval 5
```

### End-to-End Test

```bash
# 1. Start watcher
python scripts/filesystem_watcher.py . &

# 2. Drop a file
echo "Test content" > Inbox/bronze_test.txt

# 3. Wait 30 seconds

# 4. Check Needs_Action/
ls Needs_Action/

# Expected output:
# - bronze_test.txt
# - bronze_test.md
```

---

## 📝 Usage Examples

### Example 1: Process a Document

```bash
# Drop a document for processing
echo "Please summarize this meeting notes document..." > Inbox/meeting_notes.txt

# Wait for processing
# Check Needs_Action/ for the action file
# Qwen will create a summary plan
```

### Example 2: Request Approval

```bash
# Drop a file that requires approval
echo "Payment request: $500 to Vendor X" > Inbox/payment_request.txt

# Qwen will:
# 1. Read the request
# 2. Check Company_Handbook.md rules
# 3. Create approval file in Pending_Approval/
# 4. Wait for human to move to Approved/
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Watcher not detecting files | Check file permissions, verify path |
| Qwen not triggered | Verify `qwen --version` works |
| Files not moving to Done | Check approval workflow |
| Logs not appearing | Check Logs/ folder permissions |

See `BRONZE_SETUP.md` for detailed troubleshooting.

---

## ✅ Bronze Tier Checklist

- [ ] Vault folders created
- [ ] Dashboard.md displays in Obsidian
- [ ] Company_Handbook.md configured
- [ ] FileSystemWatcher runs without errors
- [ ] Orchestrator triggers Qwen
- [ ] Test file processed successfully
- [ ] Logs appearing in Logs/

---

## 📚 Next Steps

After mastering Bronze tier:

1. **Silver Tier**: Add Gmail/WhatsApp watchers
2. **MCP Integration**: Enable email sending
3. **Approval Workflow**: Human-in-the-loop
4. **Scheduled Briefings**: Weekly CEO reports

---

## 🆘 Support

- **Documentation**: `BRONZE_SETUP.md`
- **Logs**: `Logs/` folder
- **Meetings**: Wednesdays 10:00 PM PKT
- **YouTube**: https://www.youtube.com/@panaversity

---

*Bronze Tier - Foundation Complete!* 🎉


