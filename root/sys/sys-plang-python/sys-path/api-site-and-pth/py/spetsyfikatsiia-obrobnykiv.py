import sys
from importlib.machinery import FileFinder, SourceFileLoader

# Приклад реєстрації власного хука для пошуку модулів у зашифрованих контейнерах
def custom_archive_hook(path: str):
    if path.endswith(".secure_pkg"):
        # Повертаємо спеціалізований Finder для захищеного архіву
        return CustomSecureFinder(path)
    raise ImportError(f"Шлях {path} не є захищеним пакетом")

# Додавання хука на початок списку перехоплювачів
sys.path_hooks.insert(0, custom_archive_hook)

# Очищення кешу імпортерів для форсування повторного опитування
sys.path_importer_cache.clear()
