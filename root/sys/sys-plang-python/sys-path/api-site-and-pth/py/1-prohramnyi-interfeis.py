import site
import sys
from pathlib import Path

# Програмне підключення зовнішнього каталогу пакунків з обробкою його .pth файлів
known_paths = set(sys.path)
plugin_dir = Path("/opt/custom_plugins")

if plugin_dir.is_dir():
    site.addsitedir(str(plugin_dir), known_paths=known_paths)

print("Загальні каталоги site-packages:", site.getsitepackages())
print("Користувацький site-packages:", site.getusersitepackages())
print("Статус активації User Site:", site.ENABLE_USER_SITE)
