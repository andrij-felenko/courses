import os
import sys
from pathlib import Path

def get_user_data_dir(app_name: str) -> Path:
    """Повертає постійний каталог для запису даних та конфігурацій користувача."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        # Linux / POSIX стандарт XDG
        xdg_data = os.environ.get("XDG_DATA_HOME")
        base = Path(xdg_data) if xdg_data else Path.home() / ".local" / "share"
    
    app_dir = base / app_name
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir
