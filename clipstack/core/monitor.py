"""Background daemon for clipboard monitoring - Cross-platform support."""

import os
import sys
import platform
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import pyperclip
except ImportError:
    pyperclip = None

try:
    import multiprocessing
except ImportError:
    multiprocessing = None

from .storage import add_entry, CLIPSTACK_DIR, PID_PATH

# Check interval (seconds)
CHECK_INTERVAL = 0.5

# Platform detection
CURRENT_PLATFORM = platform.system()
IS_MACOS = CURRENT_PLATFORM == "Darwin"
IS_WINDOWS = CURRENT_PLATFORM == "Windows"
IS_LINUX = CURRENT_PLATFORM == "Linux"


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

    # Check if process exists (cross-platform)
    try:
        if IS_WINDOWS:
            # Windows: use tasklist or psutil
            try:
                import psutil
                return psutil.pid_exists(pid)
            except ImportError:
                # Fallback: try tasklist
                result = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True)
                return str(pid) in result.stdout.decode()
        else:
            # Unix: use os.kill with signal 0
            os.kill(pid, 0)
            return True
    except (OSError, Exception):
        return False


def run_monitor_loop() -> None:
    """Main monitoring loop (runs in daemon process)."""
    if pyperclip is None:
        print("Error: pyperclip not installed. Run: pip install pyperclip")
        return

    # Write PID
    PID_PATH.parent.mkdir(parents=True, exist_ok=True)
    PID_PATH.write_text(str(os.getpid()))

    last_content = ""

    try:
        last_content = pyperclip.paste()
    except Exception:
        last_content = ""

    while True:
        try:
            current_content = pyperclip.paste()

            if current_content != last_content and current_content:
                # New content detected
                add_entry(current_content)
                last_content = current_content

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            break
        except Exception:
            time.sleep(CHECK_INTERVAL)


def start_daemon(max_entries: int = 1000) -> bool:
    """
    Start clipboard monitoring daemon - cross-platform.

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

    CLIPSTACK_DIR.mkdir(parents=True, exist_ok=True)

    # Cross-platform daemon start
    if IS_WINDOWS:
        # Windows: use multiprocessing
        process = multiprocessing.Process(target=run_monitor_loop, daemon=True)
        process.start()
        # Save PID
        PID_PATH.write_text(str(process.pid))
        return True
    else:
        # Unix: use fork for cleaner daemon
        pid = os.fork()
        if pid == 0:
            # Child process
            os.setsid()  # Detach from parent (Unix only)
            run_monitor_loop()
            sys.exit(0)
        # Parent: save child PID
        PID_PATH.write_text(str(pid))
        return True


def stop_daemon() -> bool:
    """Stop daemon process - cross-platform."""
    pid = get_pid()
    if pid is None:
        return False

    try:
        if IS_WINDOWS:
            # Windows: use taskkill or psutil
            try:
                import psutil
                p = psutil.Process(pid)
                p.terminate()
            except ImportError:
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=False)
        else:
            # Unix: SIGTERM
            os.kill(pid, 15)

        PID_PATH.unlink(missing_ok=True)
        return True
    except (OSError, Exception):
        PID_PATH.unlink(missing_ok=True)
        return False


# ============ Auto-start Registration (Platform-specific) ============


def create_macos_launchagent() -> Path:
    """Create macOS LaunchAgent plist for auto-start."""
    plist_dir = Path.home() / "Library" / "LaunchAgents"
    plist_dir.mkdir(parents=True, exist_ok=True)

    plist_path = plist_dir / "com.clipstack.daemon.plist"

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


def create_windows_startup() -> Path:
    """Create Windows startup entry for auto-start."""
    # Windows startup folder
    startup_dir = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    startup_dir.mkdir(parents=True, exist_ok=True)

    python_path = sys.executable
    script_path = Path(__file__).parent.parent / "daemon_launcher.py"

    # Create VBS script for silent startup
    vbs_path = startup_dir / "clipstack_daemon.vbs"
    vbs_content = f"""Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "{python_path} {script_path}", 0, False
"""
    vbs_path.write_text(vbs_content)
    return vbs_path


def create_linux_systemd() -> Path:
    """Create Linux systemd service for auto-start."""
    systemd_dir = Path.home() / ".config" / "systemd" / "user"
    systemd_dir.mkdir(parents=True, exist_ok=True)

    service_path = systemd_dir / "clipstack-daemon.service"

    python_path = sys.executable
    script_path = Path(__file__).parent.parent / "daemon_launcher.py"

    service_content = f"""[Unit]
Description=Clipstack Clipboard Monitor Daemon
After=graphical-session.target

[Service]
Type=simple
ExecStart={python_path} {script_path}
Restart=on-failure

[Install]
WantedBy=default.target
"""

    service_path.write_text(service_content)
    return service_path


def register_auto_start() -> bool:
    """Register daemon for auto-start on login - cross-platform."""
    if IS_MACOS:
        plist_path = create_macos_launchagent()
        subprocess.run(["launchctl", "load", str(plist_path)], check=False)
        return True
    elif IS_WINDOWS:
        vbs_path = create_windows_startup()
        return vbs_path.exists()
    elif IS_LINUX:
        service_path = create_linux_systemd()
        subprocess.run(["systemctl", "--user", "enable", "clipstack-daemon"], check=False)
        subprocess.run(["systemctl", "--user", "start", "clipstack-daemon"], check=False)
        return True
    return False


def unregister_auto_start() -> bool:
    """Unregister auto-start - cross-platform."""
    if IS_MACOS:
        plist_path = Path.home() / "Library" / "LaunchAgents" / "com.clipstack.daemon.plist"
        if plist_path.exists():
            subprocess.run(["launchctl", "unload", str(plist_path)], check=False)
            plist_path.unlink()
        return True
    elif IS_WINDOWS:
        startup_dir = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        vbs_path = startup_dir / "clipstack_daemon.vbs"
        if vbs_path.exists():
            vbs_path.unlink()
        return True
    elif IS_LINUX:
        subprocess.run(["systemctl", "--user", "stop", "clipstack-daemon"], check=False)
        subprocess.run(["systemctl", "--user", "disable", "clipstack-daemon"], check=False)
        service_path = Path.home() / ".config" / "systemd" / "user" / "clipstack-daemon.service"
        if service_path.exists():
            service_path.unlink()
        return True
    return False


def get_auto_start_status() -> dict:
    """Get auto-start registration status."""
    status = {"platform": CURRENT_PLATFORM, "registered": False, "path": None}

    if IS_MACOS:
        plist_path = Path.home() / "Library" / "LaunchAgents" / "com.clipstack.daemon.plist"
        status["registered"] = plist_path.exists()
        status["path"] = str(plist_path) if plist_path.exists() else None
    elif IS_WINDOWS:
        startup_dir = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        vbs_path = startup_dir / "clipstack_daemon.vbs"
        status["registered"] = vbs_path.exists()
        status["path"] = str(vbs_path) if vbs_path.exists() else None
    elif IS_LINUX:
        service_path = Path.home() / ".config" / "systemd" / "user" / "clipstack-daemon.service"
        status["registered"] = service_path.exists()
        status["path"] = str(service_path) if service_path.exists() else None

    return status