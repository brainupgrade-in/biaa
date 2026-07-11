#!/usr/bin/env python3
"""Make Git Bash the default integrated terminal in VS Code (Windows).

The course's setup script and its `bash`/`source biaa-venv/Scripts/activate`
commands assume the Git Bash shell that ships with Git for Windows. This sets
VS Code's default terminal profile to "Git Bash" so every terminal a
participant opens is already the right one -- no manual selection needed.

It edits the VS Code **user** settings.json:
    %APPDATA%\\Code\\User\\settings.json          (VS Code)
    %APPDATA%\\Code - Insiders\\User\\settings.json (Insiders, if present)

Called automatically by scripts/setup-windows.sh. Safe and non-destructive:
  * Only meaningful on Windows (APPDATA set); elsewhere it's a friendly no-op
    (macOS/Linux already default to a POSIX shell).
  * If a settings.json already sets the key, it is left untouched.
  * If an existing settings.json contains comments/trailing commas (JSONC) and
    can't be parsed safely, it is NOT rewritten -- the script prints the manual
    step instead, so a participant's hand-tuned settings are never clobbered.

Usage:
  python scripts/set-vscode-terminal.py
"""
import json
import os
import sys
from pathlib import Path

KEY = "terminal.integrated.defaultProfile.windows"
VALUE = "Git Bash"
MANUAL = ("    Set it by hand: Ctrl+Shift+P -> 'Terminal: Select Default "
          "Profile' -> Git Bash")


def user_settings_paths():
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return []
    base = Path(appdata)
    return [base / "Code" / "User" / "settings.json",
            base / "Code - Insiders" / "User" / "settings.json"]


def update(path):
    """Set the default-terminal key in one settings.json. Returns a status str."""
    if path.exists():
        raw = path.read_text(encoding="utf-8-sig").strip()
        if not raw:
            data = {}
        else:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                # JSONC (comments / trailing commas) -- don't risk clobbering it.
                return f"  [skip] {path} has comments/custom formatting; not editing.\n{MANUAL}"
            if not isinstance(data, dict):
                return f"  [skip] {path} is not a settings object; not editing.\n{MANUAL}"
        if data.get(KEY) == VALUE:
            return f"  [ok] Already set in {path}"
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {}
    data[KEY] = VALUE
    path.write_text(json.dumps(data, indent=4), encoding="utf-8")
    return f"  Set '{KEY}' = '{VALUE}' in {path}"


def main():
    if os.name != "nt" or not os.environ.get("APPDATA"):
        print("  Not on Windows -- VS Code already defaults to a POSIX shell. "
              "Nothing to do.")
        return 0
    # A profile named "Git Bash" is auto-detected by VS Code when Git for
    # Windows is installed, so we only need to select it as the default.
    paths = user_settings_paths()
    # VS Code (stable) is the common case; Insiders only if its dir exists.
    targets = [paths[0]] + [p for p in paths[1:] if p.parent.exists()]
    for p in targets:
        print(update(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
