"""
File System Watcher

Monitors a drop folder for new files and creates action files in Needs_Action.
This is the simplest watcher - perfect for Bronze tier.

Usage:
    python filesystem_watcher.py /path/to/vault

Or with custom drop folder and check interval:
    python filesystem_watcher.py /path/to/vault --drop-folder /path/to/drop --interval 30
"""

import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Warning: watchdog not installed. Using polling fallback.")
    print("Install with: pip install watchdog")

from base_watcher import BaseWatcher


class DropFolderHandler(FileSystemEventHandler):
    """Handle file creation events in the drop folder."""
    
    def __init__(self, watcher: 'FileSystemWatcher'):
        self.watcher = watcher
        self.logger = watcher.logger
    
    def on_created(self, event):
        """Called when a file or directory is created."""
        if event.is_directory:
            return
        
        self.logger.info(f"File detected: {event.src_path}")
        self.watcher.process_file(Path(event.src_path))


class FileSystemWatcher(BaseWatcher):
    """
    Watches a drop folder for new files.
    
    When a file is added, it:
    1. Copies the file to Needs_Action
    2. Creates a metadata .md file with file info
    3. Logs the action
    """
    
    def __init__(
        self, 
        vault_path: str, 
        drop_folder: Optional[str] = None,
        check_interval: int = 30
    ):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            drop_folder: Path to the drop folder (default: vault/Inbox)
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        
        # Set up drop folder
        if drop_folder:
            self.drop_folder = Path(drop_folder)
        else:
            self.drop_folder = self.vault_path / 'Inbox'
        
        # Ensure drop folder exists
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files
        self.processed_files: set = set()
        
        # New files to process (for polling mode)
        self.pending_files: List[Path] = []
        
        self.logger.info(f"Drop folder: {self.drop_folder}")
    
    def check_for_updates(self) -> List[Path]:
        """
        Check for new files in the drop folder.
        
        Returns:
            List of new file paths to process
        """
        new_files = []
        
        try:
            # Scan drop folder
            for file_path in self.drop_folder.iterdir():
                if file_path.is_file() and file_path not in self.processed_files:
                    # Skip hidden files and temp files
                    if file_path.name.startswith('.') or file_path.suffix == '.tmp':
                        continue
                    
                    new_files.append(file_path)
                    self.processed_files.add(file_path)
            
            if new_files:
                self.logger.info(f"Found {len(new_files)} new file(s) in drop folder")
            
        except Exception as e:
            self.logger.error(f"Error scanning drop folder: {e}")
        
        return new_files
    
    def create_action_file(self, file_path: Path) -> Optional[Path]:
        """
        Create an action file for a dropped file.
        
        Args:
            file_path: Path to the new file
            
        Returns:
            Path to created metadata file
        """
        try:
            # Copy file to Needs_Action
            dest_path = self.needs_action / file_path.name
            
            # Handle name conflicts
            if dest_path.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                dest_path = self.needs_action / f"{file_path.stem}_{timestamp}{file_path.suffix}"
            
            shutil.copy2(file_path, dest_path)
            self.logger.info(f"Copied file to: {dest_path}")
            
            # Create metadata file
            metadata_path = self.create_metadata_file(file_path, dest_path)
            
            # Remove original from drop folder
            file_path.unlink()
            self.logger.info(f"Removed from drop folder: {file_path.name}")
            
            return metadata_path
            
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None
    
    def create_metadata_file(self, original: Path, copied: Path) -> Path:
        """
        Create a markdown metadata file for the dropped file.
        
        Args:
            original: Path to original file (before move)
            copied: Path to copied file in Needs_Action
            
        Returns:
            Path to created metadata .md file
        """
        metadata_path = copied.parent / f"{copied.stem}.md"
        
        # Get file info
        file_size = copied.stat().st_size
        file_modified = datetime.fromtimestamp(copied.stat().st_mtime).isoformat()
        
        content = f"""---
type: file_drop
original_name: {original.name}
copied_to: {copied.name}
size: {file_size}
modified: {file_modified}
created: {datetime.now().isoformat()}
status: pending
priority: normal
---

# File Drop for Processing

## File Information

| Property | Value |
|----------|-------|
| Original Name | {original.name} |
| Copied To | {copied.name} |
| Size | {self.format_size(file_size)} |
| Modified | {file_modified} |

## Content Preview

```
[File content - review and process as needed]
```

## Suggested Actions

- [ ] Review file content
- [ ] Determine required action
- [ ] Process file (update, respond, archive, etc.)
- [ ] Move to /Done when complete

## Notes

```
Add notes about processing this file
```

## Processing Log

| Date | Action | By |
|------|--------|-----|
| {datetime.now().strftime('%Y-%m-%d %H:%M')} | File received | System |
"""
        
        metadata_path.write_text(content, encoding='utf-8')
        self.logger.info(f"Created metadata file: {metadata_path.name}")
        
        return metadata_path
    
    def format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def process_file(self, file_path: Path) -> None:
        """
        Process a single file (called by event handler in watchdog mode).
        
        Args:
            file_path: Path to the new file
        """
        if file_path in self.processed_files:
            return
        
        self.logger.info(f"Processing file: {file_path.name}")
        self.processed_files.add(file_path)
        
        # Create action file
        self.create_action_file(file_path)
    
    def run_with_watchdog(self) -> None:
        """Run using watchdog event-based monitoring."""
        from watchdog.observers import Observer
        
        self.logger.info("Starting FileSystemWatcher (event-based mode)")
        self.logger.info(f"Watching: {self.drop_folder}")
        self.logger.info("Press Ctrl+C to stop")
        
        event_handler = DropFolderHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.drop_folder), recursive=False)
        observer.start()
        
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            self.logger.info("Watcher stopped by user")
        observer.join()
    
    def run_with_polling(self) -> None:
        """Run using polling-based monitoring (fallback)."""
        self.logger.info("Starting FileSystemWatcher (polling mode)")
        self.logger.info(f"Watching: {self.drop_folder}")
        self.logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                items = self.check_for_updates()
                
                if items:
                    self.logger.info(f"Found {len(items)} new file(s)")
                    for item in items:
                        self.create_action_file(item)
                else:
                    self.logger.debug("No new files")
                
                import time
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Watcher stopped by user")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Monitor a drop folder for new files and create action files.'
    )
    parser.add_argument(
        'vault_path',
        help='Path to the Obsidian vault root'
    )
    parser.add_argument(
        '--drop-folder', '-d',
        help='Path to the drop folder (default: vault/Inbox)'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=30,
        help='Check interval in seconds (default: 30)'
    )
    parser.add_argument(
        '--watchdog',
        action='store_true',
        help='Use watchdog event-based monitoring (requires watchdog package)'
    )
    
    args = parser.parse_args()
    
    # Create watcher
    watcher = FileSystemWatcher(
        vault_path=args.vault_path,
        drop_folder=args.drop_folder,
        check_interval=args.interval
    )
    
    # Run watcher
    if args.watchdog and WATCHDOG_AVAILABLE:
        watcher.run_with_watchdog()
    else:
        watcher.run_with_polling()


if __name__ == "__main__":
    main()
