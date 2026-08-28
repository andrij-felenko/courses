import sys
import types
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec


class InMemoryLoader(Loader):
    """Завантажувач, що транслює та виконує код безпосередньо з оперативної пам'яті."""

    def __init__(self, source_code: str, is_package: bool = False):
        self.source_code = source_code
        self.is_package = is_package

    def create_module(self, spec: ModuleSpec) -> types.ModuleType | None:
        """Створення об'єкта модуля.
        
        Повернення None сигналізує CPython про використання стандартного
        конструктора types.ModuleType(spec.name).
        """
        return None

    def exec_module(self, module: types.ModuleType) -> None:
        """Виконання скомпільованого коду всередині простору імен модуля."""
        origin = module.__spec__.origin or "<virtual-memory>"
        
        # Компіляція вихідного тексту в об'єкт байткоду PyCodeObject
        code_object = compile(
            self.source_code,
            filename=origin,
            mode="exec",
            dont_inherit=True,
            optimize=sys.flags.optimize,
        )

        # Виконання коду у просторі імен створеного модуля
        exec(code_object, module.__dict__)

    def get_source(self, fullname: str) -> str:
        """Повертає вихідний текст модуля для модулів inspect і linecache."""
        return self.source_code

    def get_code(self, fullname: str) -> types.CodeType:
        """Повертає скомпільований PyCodeObject без повторного виклику exec."""
        return compile(self.source_code, f"<memory://{fullname}>", "exec")


class InMemoryFinder(MetaPathFinder):
    """Знахідник мета-шляху для виявлення модулів у віртуальному реєстрі пам'яті."""

    def __init__(self, registry: dict[str, dict]):
        # registry: {"fullname": {"source": "...", "is_pkg": bool}}
        self.registry = registry

    def find_spec(
        self,
        fullname: str,
        path: list[str] | None = None,
        target: types.ModuleType | None = None,
    ) -> ModuleSpec | None:
        """Пошук специфікації модуля за повним кваліфікованим ім'ям."""
        if fullname not in self.registry:
            # Модуль не зареєстрований у нашому віртуальному сховищі
            return None

        entry = self.registry[fullname]
        source = entry.get("source", "")
        is_pkg = entry.get("is_pkg", False)

        loader = InMemoryLoader(source_code=source, is_package=is_pkg)
        origin = f"<memory://{fullname}>"

        spec = ModuleSpec(
            name=fullname,
            loader=loader,
            origin=origin,
            is_package=is_pkg,
        )

        # Якщо об'єкт є пакунком, ініціалізуємо список шляхів пошуку підмодулів
        if is_pkg:
            spec.submodule_search_locations = [origin]

        return spec


# Демонстрація підключення та виконання віртуального імпорту
if __name__ == "__main__":
    # Формуємо віртуальне дерево модулів у пам'яті
    virtual_storage = {
        "vpkg": {
            "source": "VERSION = '2.4.0'\nCONFIG = {'mode': 'memory'}",
            "is_pkg": True,
        },
        "vpkg.calc": {
            "source": (
                "import math\n"
                "def hypotenuse(a, b):\n"
                "    return math.sqrt(a**2 + b**2)\n"
            ),
            "is_pkg": False,
        },
    }

    # Реєструємо знахідник на початку sys.meta_path
    importer = InMemoryFinder(virtual_storage)
    sys.meta_path.insert(0, importer)

    # Виконуємо звичайний імпорт
    import vpkg
    from vpkg import calc

    print(f"Імпортовано пакунок: {vpkg.__name__} (v{vpkg.VERSION})")
    distance = calc.hypotenuse(6.0, 8.0)
    print(f"Результат обчислення: {distance}")
    print(f"Специфікація: {calc.__spec__}")
