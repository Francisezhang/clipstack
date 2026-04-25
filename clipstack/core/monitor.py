"""Background daemon for clipboard monitoring."""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import pyperclip
except ImportError:
    pyperclip = None

from .storage import add_entry, CLIPSTACK_DIR, PID_PATH

# Check interval (seconds)
CHECK_INTERVAL = 0.5


def get_pid() -> Optional[int]:
    """Get daemon PID if running."""
    if PID_PATH.exists():
        try:
            return int(PID_PATH.read_text().strip())
        except ValueError:
            return None
    return None


def is_running() -> bool:
    """Check if daemon is running."""
    pid = get_pid()
    if pid is None:
        return False

    # Check if process exists
    try:
        os.kill(pid, 0)  # Signal 0 just checks if process exists
        return True
    except OSError:
        return False


def start_daemon(max_entries: int = 1000) -> bool:
    """
    Start clipboard monitoring daemon.

    Args:
        max_entries: Maximum entries to keep

    Returns:
        True if started successfully
    """
    if is_running():
        return False

    if pyperclip is None:
        print("Error: pyperclip not installed. Run: pip install pyperclip")
        return False

    # Start daemon process
    daemon_script = Path(__file__).parent / "monitor_daemon.py"

    # Fork to background
    pid = os.fork()
    if pid == 0:
        # Child process - run daemon
        os.setsid()  # Detach from parent

        # Write PID
        PID_PATH.write_text(str(os.getpid()))

        # Run monitoring loop
        run_monitor_loop()
        sys.exit(0)

    return True


def stop_daemon() -> bool:
    """Stop daemon process."""
    pid = get_pid()
    if pid is None:
        return False

    try:
        os.kill(pid, 15)  # SIGTERM
        PID_PATH.unlink()
        return True
    except OSError:
        PID_PATH.unlink()
        return False


def run_monitor_loop() -> None:
    """Main monitoring loop (runs in daemon process)."""
    if pyperclip is None:
        return

    last_content = pyperclip.paste()

    while True:
        try:
            current_content = pyperclip.paste()

            if current_content != last_content and current_content:
                # New content detected
                add_entry(current_content)
                last_content = current_content

            time.sleep(CHECK_INTERVAL)

        except Exception:
            # Handle errors gracefully
            time.sleep(CHECK_INTERVAL)


def create_launchctl_plist() -> Path:
    """
    Create launchctl plist for auto-start on login.

    Returns:
        Path to plist file
    """
    plist_dir = Path.home() / "Library" / "LaunchAgents"
    plist_dir.mkdir(parents=True, exist_ok=True)

    plist_path = plist_dir / "com.clipstack.daemon.plist"

    # Get python and script paths
    python_path = sys.executable
    script_path = Path(__file__).parent.parent / "daemon_launcher.py"

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.clipstack.daemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/clipstack.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/clipstack.err</string>
</dict>
</plist>
"""

    plist_path.write_text(plist_content)
    return plist_path


def register_launchctl_service() -> bool:
    """Register daemon as macOS LaunchAgent."""
    plist_path = create_launchctl_plist()

    subprocess.run(["launchctl", "load", str(plist_path)], check=True)
    return True


def unregister_launchctl_service() -> bool:
    """Unregister LaunchAgent."""
    plist_path = Path.home() / "Library" / "LaunchAgents" / "com.clipstack.daemon.plist"

    if plist_path.exists():
        subprocess.run(["launchctl", "unload", str(plist_path)], check=False)
        plist_path.unlink()

    return True