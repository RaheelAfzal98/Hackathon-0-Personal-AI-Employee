"""
Ralph Wiggum Plugin for AI Employee

This plugin keeps Claude Code working autonomously until tasks are complete.
It intercepts Claude's exit and re-injects the prompt if work remains.

Installation:
1. Copy this file to: <vault>/.claude/plugins/ralph_wiggum.py
2. Run Claude Code from the vault directory
3. Use /ralph-loop command to start persistent mode

Usage:
    /ralph-loop "Process all files in /Needs_Action" --max-iterations 10
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple


class RalphWiggumPlugin:
    """
    Ralph Wiggum persistence plugin.
    
    Named after the Simpsons character who never gives up,
    this plugin ensures Claude Code continues working until
    tasks are truly complete.
    """
    
    def __init__(self, vault_path: str, max_iterations: int = 10):
        """
        Initialize the Ralph Wiggum plugin.
        
        Args:
            vault_path: Path to the Obsidian vault
            max_iterations: Maximum loop iterations before forcing exit
        """
        self.vault_path = Path(vault_path)
        self.max_iterations = max_iterations
        self.iteration_count = 0
        
        # State file paths
        self.state_dir = self.vault_path / '.claude' / 'state'
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.iteration_file = self.state_dir / 'ralph_iteration.txt'
        self.prompt_file = self.state_dir / 'ralph_prompt.txt'
        self.done_file = self.state_dir / 'task_complete.flag'
        
        # Load current iteration
        self._load_state()
    
    def _load_state(self) -> None:
        """Load current iteration count from state file."""
        if self.iteration_file.exists():
            try:
                self.iteration_count = int(self.iteration_file.read_text().strip())
            except ValueError:
                self.iteration_count = 0
    
    def _save_state(self) -> None:
        """Save current iteration count to state file."""
        self.iteration_file.write_text(str(self.iteration_count))
        self.prompt_file.write_text(datetime.now().isoformat())
    
    def _clear_state(self) -> None:
        """Clear all state files."""
        for f in [self.iteration_file, self.prompt_file, self.done_file]:
            if f.exists():
                f.unlink()
    
    def check_task_complete(self) -> bool:
        """
        Check if the current task is complete.
        
        Returns:
            True if task is complete (all items processed)
        """
        needs_action = self.vault_path / 'Needs_Action'
        
        if not needs_action.exists():
            return True
        
        # Check if there are any .md files
        md_files = [f for f in needs_action.iterdir() if f.suffix == '.md']
        
        return len(md_files) == 0
    
    def should_continue(self) -> Tuple[bool, str]:
        """
        Determine if Claude should continue working.
        
        Returns:
            Tuple of (should_continue: bool, reason: str)
        """
        # Check if task is complete
        if self.check_task_complete():
            self.done_file.write_text(f"Task completed at {datetime.now().isoformat()}")
            self._clear_state()
            return False, "Task complete - all items processed"
        
        # Check iteration limit
        if self.iteration_count >= self.max_iterations:
            self._clear_state()
            return False, f"Max iterations ({self.max_iterations}) reached"
        
        # Continue working
        self.iteration_count += 1
        self._save_state()
        
        return True, f"Continuing (iteration {self.iteration_count}/{self.max_iterations})"
    
    def get_continuation_prompt(self, original_prompt: str, last_output: str) -> str:
        """
        Generate a continuation prompt.
        
        Args:
            original_prompt: The original task prompt
            last_output: Claude's last output
            
        Returns:
            New prompt to continue working
        """
        return f"""[Ralph Wiggum Mode - Iteration {self.iteration_count}]

Previous task: {original_prompt}

Your last output was:
{last_output[:500]}...

The task is not yet complete. Review what you've done and continue working.
Check the Needs_Action folder again and process any remaining items.
If you created a plan, execute it. If actions need approval, create approval files.

Remember: Keep working until all items are processed and moved to Done."""
    
    def run_check(self) -> Optional[str]:
        """
        Run the Ralph Wiggum check.
        
        Returns:
            Continuation prompt if should continue, None if complete
        """
        should_continue, reason = self.should_continue()
        
        print(f"Ralph Wiggum: {reason}")
        
        if should_continue:
            # Return continuation signal
            return f"[Ralph Wiggum: {reason}]"
        
        return None


def ralph_loop(vault_path: str, prompt: str, max_iterations: int = 10) -> None:
    """
    Run a Ralph Wiggum loop.
    
    This is a helper function to start Ralph mode from command line.
    
    Args:
        vault_path: Path to the Obsidian vault
        prompt: The task prompt for Claude
        max_iterations: Maximum loop iterations
    """
    plugin = RalphWiggumPlugin(vault_path, max_iterations)
    
    # Save the prompt
    prompt_file = vault_path / '.claude' / 'state' / 'ralph_prompt.txt'
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file.write_text(prompt)
    
    print(f"Ralph Wiggum mode activated")
    print(f"Vault: {vault_path}")
    print(f"Max iterations: {max_iterations}")
    print(f"Task: {prompt}")
    print()
    print("Now run Claude Code with this prompt:")
    print(f"  claude --prompt \"{prompt}\"")
    print()
    print("Ralph will check if the task is complete after each run.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Ralph Wiggum persistence plugin')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('prompt', help='Task prompt for Claude')
    parser.add_argument('--max-iterations', type=int, default=10,
                       help='Maximum loop iterations')
    
    args = parser.parse_args()
    
    ralph_loop(args.vault_path, args.prompt, args.max_iterations)
