import os
from pathlib import Path
import sys

APPDATA_DIR = Path(os.getenv("LOCALAPPDATA")) / "WinTrack"
APPDATA_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_PATH = APPDATA_DIR / "config.json"
DB_PATH = APPDATA_DIR / "screen_time.db"