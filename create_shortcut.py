"""Create a Windows desktop shortcut (.lnk) for Book Page Summarizer."""

import os
import subprocess
import sys

APP_NAME = "Book Page Summarizer"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHONW = os.path.join(PROJECT_DIR, ".venv", "Scripts", "pythonw.exe")
APP_PY = os.path.join(PROJECT_DIR, "app.py")
ICON = os.path.join(PROJECT_DIR, "app.ico")
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
SHORTCUT = os.path.join(DESKTOP, f"{APP_NAME}.lnk")

ps_script = f"""
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut('{SHORTCUT}')
$sc.TargetPath = '{PYTHONW}'
$sc.Arguments = '"{APP_PY}"'
$sc.WorkingDirectory = '{PROJECT_DIR}'
$sc.IconLocation = '{ICON}'
$sc.Description = '{APP_NAME}'
$sc.Save()
"""

if __name__ == "__main__":
    if not os.path.exists(PYTHONW):
        print(f"Error: {PYTHONW} not found. Ensure the venv is set up.", file=sys.stderr)
        sys.exit(1)

    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error creating shortcut:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"Shortcut created: {SHORTCUT}")
