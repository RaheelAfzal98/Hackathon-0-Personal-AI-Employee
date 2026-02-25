# Personal AI Employee - Project Context

## Project Overview

This is a **hackathon project** focused on building a "Digital FTE" (Full-Time Equivalent) - an autonomous AI employee that manages personal and business affairs 24/7. The project uses a **local-first, agent-driven, human-in-the-loop** architecture.

### Core Concept

The AI Employee acts as a proactive business partner that:
- Monitors communications (Gmail, WhatsApp, LinkedIn)
- Manages tasks and projects
- Handles accounting and bank transactions
- Posts to social media platforms
- Generates executive briefings ("Monday Morning CEO Briefing")

### Architecture Components

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Claude Code | Reasoning engine with Ralph Wiggum persistence loop |
| **Memory/GUI** | Obsidian | Local Markdown dashboard and knowledge base |
| **Senses** | Python Watchers | Monitor Gmail, WhatsApp, filesystems |
| **Hands** | MCP Servers | External actions (email, browser automation, payments) |

## Key Technologies

- **Claude Code**: Primary AI reasoning engine
- **Obsidian**: Local Markdown vault for dashboard and memory
- **Python 3.13+**: Watcher scripts and orchestration
- **Node.js v24+**: MCP servers
- **Playwright MCP**: Browser automation (installed skill)

## Project Structure

```
Hackathon-0-Personal-AI-Employee/
├── .qwen/skills/           # Installed AI skills
│   └── browsing-with-playwright/
├── skills-lock.json        # Skill versioning
└── QWEN.md                 # This file
```

### Obsidian Vault Structure (to be created by user)

```
AI_Employee_Vault/
├── Dashboard.md            # Real-time summary
├── Company_Handbook.md     # Rules of engagement
├── Business_Goals.md       # Q1/Q2 objectives
├── Inbox/                  # New items to process
├── Needs_Action/           # Items requiring attention
├── In_Progress/            # Currently being worked on
├── Done/                   # Completed items
├── Pending_Approval/       # Awaiting human approval
├── Approved/               # Approved actions
├── Plans/                  # Generated plans
└── Briefings/              # CEO briefings
```

## Building and Running

### Prerequisites Setup

```bash
# 1. Install required software
# - Claude Code (Pro subscription or free tier)
# - Obsidian v1.10.6+
# - Python 3.13+
# - Node.js v24+ LTS
# - GitHub Desktop

# 2. Create Obsidian vault
# Name it "AI_Employee_Vault"

# 3. Verify Claude Code
claude --version

# 4. Set up Python project with UV
uv init
```

### Playwright MCP (Browser Automation)

The project includes a `browsing-with-playwright` skill for web automation:

```bash
# Start the Playwright MCP server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify it's running
python3 .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop the server when done
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### Watcher Scripts (to be implemented)

Create Python watcher scripts following the base pattern:

```python
# base_watcher.py - Template
from pathlib import Path
from abc import ABC, abstractmethod
import time

class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        
    @abstractmethod
    def check_for_updates(self) -> list:
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        pass
    
    def run(self):
        while True:
            items = self.check_for_updates()
            for item in items:
                self.create_action_file(item)
            time.sleep(self.check_interval)
```

### Ralph Wiggum Loop (Persistence)

Use the Ralph Wiggum pattern to keep Claude working until tasks complete:

```bash
# Start a Ralph loop
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

## Development Tiers

| Tier | Description | Estimated Time |
|------|-------------|----------------|
| **Bronze** | Foundation (1 watcher, basic vault) | 8-12 hours |
| **Silver** | Functional Assistant (2+ watchers, MCP) | 20-30 hours |
| **Gold** | Autonomous Employee (full integration) | 40+ hours |
| **Platinum** | Always-On Cloud + Local Executive | 60+ hours |

## Key Patterns

### Human-in-the-Loop (HITL)

For sensitive actions, Claude writes an approval request file instead of acting directly:

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
status: pending
---

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

### Claim-by-Move Rule

Prevents double-work in multi-agent scenarios:
- First agent to move an item from `/Needs_Action` to `/In_Progress/<agent>/` owns it
- Other agents must ignore it

### Security Rules

- Vault sync includes only markdown/state files
- Secrets never sync (`.env`, tokens, WhatsApp sessions, banking credentials)
- Cloud agents work in draft-only mode; Local executes final actions

## MCP Servers

Recommended MCP servers for different capabilities:

| Server | Capabilities | Use Case |
|--------|-------------|----------|
| `filesystem` | Read, write, list files | Built-in for vault |
| `email-mcp` | Send, draft, search emails | Gmail integration |
| `browser-mcp` | Navigate, click, fill forms | Payment portals |
| `calendar-mcp` | Create, update events | Scheduling |
| `slack-mcp` | Send messages, read channels | Team communication |

## Testing Practices

1. **Unit Testing**: Test individual watcher scripts in isolation
2. **Integration Testing**: Verify watcher → Claude → MCP flow
3. **E2E Testing**: Run full autonomous cycles with sample data
4. **Verification**: Use `verify.py` scripts for MCP servers

## Common Commands

```bash
# Start browser automation
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Run a watcher script
python watchers/gmail_watcher.py

# Trigger Claude Code processing
claude "Check /Needs_Action and process pending items"

# Generate weekly briefing
claude "Read Business_Goals.md and generate Monday Morning CEO Briefing"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Playwright MCP not responding | Run `stop-server.sh` then `start-server.sh` |
| Element not found in browser | Run `browser_snapshot` first to get current refs |
| Claude exits prematurely | Use Ralph Wiggum loop for persistence |
| Watcher not detecting changes | Check file permissions and paths |
| Approval workflow stuck | Verify file movement between folders |

## Resources

- [Claude Code Documentation](https://claude.com/product/claude-code)
- [Obsidian Download](https://obsidian.md/download)
- [Agent Skills Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Ralph Wiggum Plugin](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- [Playwright MCP Reference](.qwen/skills/browsing-with-playwright/references/playwright-tools.md)

## Meeting Schedule

**Research and Showcase Meeting**: Every Wednesday at 10:00 PM PKT on Zoom
- First meeting: Wednesday, January 7th, 2026
- YouTube: https://www.youtube.com/@panaversity
