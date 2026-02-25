"""
Base Watcher Module

Abstract base class for all watcher scripts in the AI Employee system.
All watchers follow the same pattern: monitor → detect → create action file.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional


class BaseWatcher(ABC):
    """
    Abstract base class for all AI Employee watchers.
    
    Watchers are long-running processes that monitor external sources
    (Gmail, WhatsApp, file systems, etc.) and create action files in
    the Needs_Action folder when something requires attention.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Ensure Needs_Action directory exists
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
        # Track processed items to avoid duplicates
        self.processed_ids: set = set()
        
        self.logger.info(f"Initialized {self.__class__.__name__}")
        self.logger.info(f"Vault path: {self.vault_path}")
        self.logger.info(f"Check interval: {check_interval}s")
    
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check the external source for new items.
        
        Returns:
            List of new items that need processing
            
        Example:
            For Gmail: List of message objects
            For WhatsApp: List of message dicts
            For File System: List of new file paths
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a markdown action file in Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to created file, or None if creation failed
            
        The action file should include:
            - YAML frontmatter with type, source, timestamp, priority
            - Original content/data
            - Suggested actions as checkboxes
        """
        pass
    
    def run(self) -> None:
        """
        Main run loop for the watcher.
        
        Continuously checks for updates and creates action files.
        Runs until interrupted (Ctrl+C).
        """
        self.logger.info(f"Starting {self.__class__.__name__}")
        self.logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                try:
                    # Check for new items
                    items = self.check_for_updates()
                    
                    if items:
                        self.logger.info(f"Found {len(items)} new item(s)")
                        
                        for item in items:
                            filepath = self.create_action_file(item)
                            if filepath:
                                self.logger.info(f"Created action file: {filepath.name}")
                    else:
                        self.logger.debug("No new items")
                    
                except Exception as e:
                    self.logger.error(f"Error processing items: {e}", exc_info=True)
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f"{self.__class__.__name__} stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
            raise
        finally:
            self.logger.info(f"{self.__class__.__name__} shutting down")
    
    def generate_filename(self, prefix: str, unique_id: str) -> str:
        """
        Generate a unique filename for an action file.
        
        Args:
            prefix: Type prefix (e.g., 'EMAIL', 'WHATSAPP', 'FILE')
            unique_id: Unique identifier for the item
            
        Returns:
            Filename string with .md extension
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Sanitize unique_id for filesystem
        safe_id = ''.join(c if c.isalnum() or c in '-_' else '_' for c in unique_id)
        return f"{prefix}_{safe_id}_{timestamp}.md"
    
    def create_frontmatter(self, item_type: str, **kwargs) -> str:
        """
        Create YAML frontmatter for action files.
        
        Args:
            item_type: Type of item (email, whatsapp, file_drop, etc.)
            **kwargs: Additional frontmatter fields
            
        Returns:
            YAML frontmatter string including --- delimiters
        """
        frontmatter = [
            "---",
            f"type: {item_type}",
            f"created: {datetime.now().isoformat()}",
            f"status: pending",
        ]
        
        # Add optional fields
        if 'priority' in kwargs:
            frontmatter.append(f"priority: {kwargs['priority']}")
        if 'source' in kwargs:
            frontmatter.append(f"source: {kwargs['source']}")
        if 'from' in kwargs:
            frontmatter.append(f"from: {kwargs['from']}")
        if 'subject' in kwargs:
            frontmatter.append(f"subject: {kwargs['subject']}")
            
        frontmatter.append("---")
        return "\n".join(frontmatter)


if __name__ == "__main__":
    # Example usage / testing
    print("BaseWatcher is an abstract class.")
    print("Subclass it to create specific watchers.")
    print("\nExample subclasses:")
    print("  - GmailWatcher")
    print("  - WhatsAppWatcher")
    print("  - FileSystemWatcher")
