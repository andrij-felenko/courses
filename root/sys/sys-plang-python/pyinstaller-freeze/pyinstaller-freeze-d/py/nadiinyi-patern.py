import sys
from pathlib import Path

def get_bundle_dir() -> Path:
    """
    Повертає базовий каталог розпакованих або локальних ресурсів застосунку.
    Працює однаково надійно у сирцевому режимі (.py), у режимі --onedir та --onefile.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Режим замороженого файлу (PyInstaller): повертаємо тимчасову теку _MEI
        return Path(sys._MEIPASS)
    
    # Звичайний режим виконання через python main.py
    return Path(__file__).resolve().parent

def resolve_asset_path(relative_asset_path: str) -> Path:
    """Знаходить вшитий файл ресурсів (зображення, сертифікат, шаблон)."""
    target = get_bundle_dir() / relative_asset_path
    if not target.exists():
        raise FileNotFoundError(f"Вбудований ресурс не знайдено: {target}")
    return target
