"""
Bronze Tier Verification Script

Run this script to verify that all Bronze Tier components are properly set up.

Usage:
    python verify_bronze.py /path/to/vault
"""

import sys
from pathlib import Path
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    CHECK = '[OK]'
    CROSS = '[FAIL]'


def check(condition: bool, message: str) -> bool:
    """Print check result and return condition."""
    if condition:
        print(f"  {Colors.GREEN}{Colors.CHECK} {message}{Colors.RESET}")
    else:
        print(f"  {Colors.RED}{Colors.CROSS} {message}{Colors.RESET}")
    return condition


def verify_vault(vault_path: Path) -> bool:
    """Verify vault structure and files."""
    print(f"\n{Colors.BLUE}Verifying Vault: {vault_path}{Colors.RESET}\n")
    
    all_passed = True
    
    # Check required folders
    print("Required Folders:")
    required_folders = [
        'Inbox', 'Needs_Action', 'Done', 'Plans',
        'Pending_Approval', 'Approved', 'Logs'
    ]
    for folder in required_folders:
        exists = (vault_path / folder).exists()
        all_passed &= check(exists, f"{folder}/")
    
    # Check required files
    print("\nCore Files:")
    required_files = [
        'Dashboard.md',
        'Company_Handbook.md',
        'Business_Goals.md',
        'README.md',
        'BRONZE_SETUP.md'
    ]
    for file in required_files:
        exists = (vault_path / file).exists()
        all_passed &= check(exists, file)
    
    # Check scripts
    print("\nPython Scripts:")
    required_scripts = [
        'scripts/base_watcher.py',
        'scripts/filesystem_watcher.py',
        'scripts/orchestrator.py',
        'scripts/requirements.txt'
    ]
    for script in required_scripts:
        exists = (vault_path / script).exists()
        all_passed &= check(exists, script)
    
    # Check Ralph Wiggum plugin
    print("\nRalph Wiggum Plugin:")
    ralph_files = [
        '.claude/plugins/ralph_wiggum.py',
        '.claude/ralph_config.yaml'
    ]
    for file in ralph_files:
        exists = (vault_path / file).exists()
        all_passed &= check(exists, file)
    
    # Check helper scripts
    print("\nHelper Scripts:")
    helper_files = [
        'start.bat',
        'stop.bat'
    ]
    for file in helper_files:
        exists = (vault_path / file).exists()
        all_passed &= check(exists, file)
    
    # Check Python syntax
    print("\nPython Syntax Check:")
    import subprocess
    scripts_to_check = [
        'scripts/base_watcher.py',
        'scripts/filesystem_watcher.py',
        'scripts/orchestrator.py'
    ]
    for script in scripts_to_check:
        script_path = vault_path / script
        if script_path.exists():
            result = subprocess.run(
                ['python', '-m', 'py_compile', str(script_path)],
                capture_output=True,
                text=True
            )
            all_passed &= check(result.returncode == 0, f"{script} syntax")
        else:
            all_passed &= check(False, f"{script} (missing)")
    
    return all_passed


def verify_dashboard_content(vault_path: Path) -> bool:
    """Verify Dashboard.md has required sections."""
    print(f"\n{Colors.BLUE}Verifying Dashboard Content{Colors.RESET}\n")
    
    dashboard = vault_path / 'Dashboard.md'
    if not dashboard.exists():
        print(f"  {Colors.RED}{Colors.CROSS} Dashboard.md not found{Colors.RESET}")
        return False
    
    content = dashboard.read_text(encoding='utf-8')
    
    checks = [
        ('Quick Stats' in content, 'Quick Stats section'),
        ('Pending Items' in content, 'Pending Items metric'),
        ('Financial Snapshot' in content, 'Financial Snapshot'),
        ('Business Goals' in content, 'Business Goals'),
    ]
    
    all_passed = True
    for condition, message in checks:
        all_passed &= check(condition, message)
    
    return all_passed


def verify_handbook_content(vault_path: Path) -> bool:
    """Verify Company_Handbook.md has required sections."""
    print(f"\n{Colors.BLUE}Verifying Company Handbook Content{Colors.RESET}\n")
    
    handbook = vault_path / 'Company_Handbook.md'
    if not handbook.exists():
        print(f"  {Colors.RED}{Colors.CROSS} Company_Handbook.md not found{Colors.RESET}")
        return False
    
    content = handbook.read_text(encoding='utf-8')
    
    checks = [
        ('Core Principles' in content, 'Core Principles section'),
        ('Financial Rules' in content, 'Financial Rules'),
        ('Privacy' in content, 'Privacy rules'),
        ('Red Flags' in content, 'Red Flags - escalation rules'),
        ('Decision Matrix' in content, 'Decision Matrix'),
    ]
    
    all_passed = True
    for condition, message in checks:
        all_passed &= check(condition, message)
    
    return all_passed


def main():
    """Main verification function."""
    print(f"{Colors.GREEN}")
    print("=" * 60)
    print("  AI Employee - Bronze Tier Verification")
    print("=" * 60)
    print(f"{Colors.RESET}")
    
    # Get vault path
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    else:
        vault_path = Path('.')
    
    if not vault_path.exists():
        print(f"{Colors.RED}Error: Vault path does not exist: {vault_path}{Colors.RESET}")
        sys.exit(1)
    
    # Run verifications
    vault_ok = verify_vault(vault_path)
    dashboard_ok = verify_dashboard_content(vault_path)
    handbook_ok = verify_handbook_content(vault_path)
    
    # Summary
    print(f"\n{Colors.BLUE}")
    print("=" * 60)
    print("  Verification Summary")
    print("=" * 60)
    print(f"{Colors.RESET}")
    
    all_passed = vault_ok and dashboard_ok and handbook_ok

    if all_passed:
        print(f"{Colors.GREEN}  [PASS] All Bronze Tier checks passed!{Colors.RESET}")
        print(f"\n  {Colors.GREEN}Bronze Tier Status: COMPLETE{Colors.RESET}")
        print(f"\n  Next steps:")
        print(f"  1. Install dependencies: pip install -r scripts/requirements.txt")
        print(f"  2. Start the system: start.bat .")
        print(f"  3. Drop a test file in Inbox/")
        print(f"  4. Watch the AI Employee work!")
    else:
        print(f"{Colors.RED}  [FAIL] Some checks failed. Review output above.{Colors.RESET}")
        print(f"\n  {Colors.YELLOW}Bronze Tier Status: INCOMPLETE{Colors.RESET}")
        print(f"\n  Fix the issues above and run verification again.")
    
    print()
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

