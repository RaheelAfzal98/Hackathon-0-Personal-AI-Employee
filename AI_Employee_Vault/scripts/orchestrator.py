"""
Orchestrator - Master Process for AI Employee

The orchestrator:
1. Monitors folders for items needing attention
2. Triggers Qwen Code to process items
3. Manages the Ralph Wiggum persistence loop
4. Updates the Dashboard.md with current status
5. Handles approved actions

Usage:
    python orchestrator.py /path/to/vault

Or with options:
    python orchestrator.py /path/to/vault --interval 60 --dry-run
"""

import sys
import shutil
import argparse
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import logging


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.

    Coordinates between watchers, Qwen Code, and action execution.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60, dry_run: bool = False):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between orchestration cycles
            dry_run: If True, log actions but don't execute them
        """
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval
        self.dry_run = dry_run
        
        # Folder paths
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure all folders exist
        for folder in [self.inbox, self.needs_action, self.plans, 
                       self.pending_approval, self.approved, self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger('Orchestrator')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Also log to file
        log_file = self.logs / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        self.logger.info(f"Orchestrator initialized")
        self.logger.info(f"Vault: {self.vault_path}")
        self.logger.info(f"Dry run: {dry_run}")
    
    def count_items(self, folder: Path) -> int:
        """Count .md files in a folder."""
        if not folder.exists():
            return 0
        return len([f for f in folder.iterdir() if f.suffix == '.md'])
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get current stats for dashboard."""
        return {
            'pending_items': self.count_items(self.needs_action),
            'plans': self.count_items(self.plans),
            'pending_approval': self.count_items(self.pending_approval),
            'approved': self.count_items(self.approved),
            'done_today': self.count_items_done_today(),
        }
    
    def count_items_done_today(self) -> int:
        """Count items moved to Done today."""
        if not self.done.exists():
            return 0
        
        today = datetime.now().strftime('%Y-%m-%d')
        count = 0
        for f in self.done.iterdir():
            if f.suffix == '.md':
                try:
                    content = f.read_text(encoding='utf-8')
                    if today in content:
                        count += 1
                except:
                    pass
        return count
    
    def update_dashboard(self) -> None:
        """Update Dashboard.md with current stats."""
        if not self.dashboard.exists():
            self.logger.warning("Dashboard.md not found")
            return
        
        stats = self.get_dashboard_stats()
        
        try:
            content = self.dashboard.read_text(encoding='utf-8')
            
            # Update stats table
            lines = content.split('\n')
            new_lines = []
            in_stats = False
            
            for line in lines:
                if '| Pending Items |' in line:
                    new_lines.append(f"| Pending Items | {stats['pending_items']} |")
                    in_stats = True
                elif '| In Progress |' in line:
                    new_lines.append(f"| In Progress | {stats['plans']} |")
                elif '| Completed Today |' in line:
                    new_lines.append(f"| Completed Today | {stats['done_today']} |")
                elif '| Awaiting Approval |' in line:
                    new_lines.append(f"| Awaiting Approval | {stats['pending_approval']} |")
                else:
                    new_lines.append(line)
            
            # Add timestamp
            new_content = '\n'.join(new_lines)
            new_content = new_content.replace(
                'last_updated:', 
                f'last_updated: {datetime.now().isoformat()}'
            )
            
            if not self.dry_run:
                self.dashboard.write_text(new_content, encoding='utf-8')
            
            self.logger.info("Dashboard updated")
            
        except Exception as e:
            self.logger.error(f"Error updating dashboard: {e}")
    
    def get_pending_items(self) -> List[Path]:
        """Get list of pending items in Needs_Action."""
        if not self.needs_action.exists():
            return []
        return [f for f in self.needs_action.iterdir() if f.suffix == '.md']
    
    def get_approved_items(self) -> List[Path]:
        """Get list of approved items ready for action."""
        if not self.approved.exists():
            return []
        return [f for f in self.approved.iterdir() if f.suffix == '.md']
    
    def create_qwen_prompt(self, items: List[Path]) -> str:
        """
        Create a prompt for Qwen Code to process items.

        Args:
            items: List of action files to process

        Returns:
            Prompt string for Qwen Code
        """
        item_list = '\n'.join([f"- {item.name}" for item in items])

        prompt = f"""You are the AI Employee. Process the following {len(items)} item(s) in the Needs_Action folder:

{item_list}

For each item:
1. Read the file content carefully
2. Determine what action is needed based on the Company_Handbook.md rules
3. If the action requires approval (per handbook rules), create a file in Pending_Approval/
4. If the action can be done autonomously, create a Plan.md file in Plans/ with checkboxes
5. Update Dashboard.md with progress
6. When complete, move processed files to Done/

Remember the rules from Company_Handbook.md:
- Always be polite and professional
- Flag payments over $50 for approval
- Never share credentials
- Response time target: 24 hours
- Escalate emotional/sensitive content

Start by reading Company_Handbook.md and Business_Goals.md for context, then process each item."""

        return prompt
    
    def trigger_qwen(self, prompt: str) -> bool:
        """
        Trigger Qwen Code to process items.

        Args:
            prompt: The prompt to give Qwen Code

        Returns:
            True if Qwen Code was triggered successfully
        """
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would trigger Qwen Code with prompt: {prompt[:100]}...")
            return True

        try:
            # Change to vault directory and run Qwen Code
            # On Windows, use shell=True and command string to find .cmd scripts
            import platform
            use_shell = platform.system() == 'Windows'
            
            if use_shell:
                # On Windows, command must be a string when shell=True
                cmd = f'qwen "{prompt}"'
            else:
                # On Unix-like systems, use list with shell=False
                cmd = ['qwen', prompt]
            
            result = subprocess.run(
                cmd,
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                shell=use_shell
            )

            if result.returncode == 0:
                self.logger.info("Qwen Code processing completed successfully")
                return True
            else:
                self.logger.error(f"Qwen Code error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("Qwen Code processing timed out (5 minutes)")
            return False
        except FileNotFoundError:
            self.logger.error("Qwen Code not found. Make sure it's installed and in PATH.")
            self.logger.error("Install Qwen Code first.")
            return False
        except Exception as e:
            self.logger.error(f"Error triggering Qwen Code: {e}")
            return False
    
    def process_approved_items(self) -> None:
        """Process items that have been approved by human."""
        approved = self.get_approved_items()
        
        if not approved:
            return
        
        self.logger.info(f"Processing {len(approved)} approved item(s)")
        
        for item in approved:
            try:
                content = item.read_text(encoding='utf-8')
                
                # Parse the approval file to determine action
                # For Bronze tier, we just log the approval
                self.logger.info(f"Approved item processed: {item.name}")
                
                # Move to Done
                if not self.dry_run:
                    dest = self.done / item.name
                    shutil.move(str(item), str(dest))
                    
            except Exception as e:
                self.logger.error(f"Error processing approved item {item.name}: {e}")
    
    def log_action(self, action_type: str, details: Dict[str, Any]) -> None:
        """
        Log an action to the logs folder.

        Args:
            action_type: Type of action (e.g., 'orchestrate', 'qwen_trigger')
            details: Dictionary of action details
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'orchestrator',
            **details
        }
        
        log_file = self.logs / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        
        try:
            # Append to existing log file or create new
            if log_file.exists():
                logs = json.loads(log_file.read_text(encoding='utf-8'))
            else:
                logs = []
            
            logs.append(log_entry)
            
            if not self.dry_run:
                log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')
                
        except Exception as e:
            self.logger.error(f"Error logging action: {e}")
    
    def run_cycle(self) -> None:
        """Run one orchestration cycle."""
        self.logger.info("Starting orchestration cycle")

        # Update dashboard
        self.update_dashboard()

        # Check for pending items
        pending = self.get_pending_items()

        if pending:
            self.logger.info(f"Found {len(pending)} pending item(s)")

            # Create prompt and trigger Qwen Code
            prompt = self.create_qwen_prompt(pending)
            self.trigger_qwen(prompt)

            self.log_action('qwen_trigger', {
                'items_count': len(pending),
                'items': [item.name for item in pending]
            })
        else:
            self.logger.debug("No pending items")

        # Process approved items
        self.process_approved_items()

        # Final dashboard update
        self.update_dashboard()

        self.logger.info("Orchestration cycle complete")
    
    def run(self) -> None:
        """Run the orchestrator continuously."""
        self.logger.info(f"Starting Orchestrator (interval: {self.check_interval}s)")
        self.logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                self.run_cycle()
                
                import time
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Orchestrator stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
            raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Orchestrate AI Employee actions between watchers and Qwen Code.'
    )
    parser.add_argument(
        'vault_path',
        help='Path to the Obsidian vault root'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='Orchestration interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Log actions but do not execute them'
    )

    args = parser.parse_args()

    orchestrator = Orchestrator(
        vault_path=args.vault_path,
        check_interval=args.interval,
        dry_run=args.dry_run
    )

    orchestrator.run()


if __name__ == "__main__":
    main()
