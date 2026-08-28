import sys
import types
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec


class VirtualCodeLoader(Loader):
    """Завантажувач коду з віртуального сховища пам'яті."""

    def __init__(self, source_code: str):
        self.source_code = source_code

    def create_module(self, spec: ModuleSpec) -> types.ModuleType | None:
        # Повертаємо None: CPython самостійно створить об'єкт types.ModuleType
        return None

    def exec_module(self, module: types.ModuleType) -> None:
        # Компілюємо вихідний текст у просторі імен модуля
        origin = module.__spec__.origin or "<virtual>"
        code_obj = compile(self.source_code, origin, "exec")
        exec(code_obj, module.__dict__)


class VirtualPathFinder(MetaPathFinder):
    """Знахідник мета-шляху для віртуальних модулів."""

    def __init__(self, code_registry: dict[str, str]):
        self.code_registry = code_registry

    def find_spec(
        self,
        fullname: str,
        path: list[str] | None = None,
        target: types.ModuleType | None = None,
    ) -> ModuleSpec | None:
        if fullname in self.code_registry:
            source = self.code_registry[fullname]
            loader = VirtualCodeLoader(source)
            return ModuleSpec(
                name=fullname,
                loader=loader,
                origin=f"<virtual://{fullname}>",
                is_package=False,
            )
        return None


# Реєстрація власного знахідника на початку системного списку
storage = {
    "telemetry_client": "def send_ping(): return {'status': 'ok', 'code': 200}"
}

sys.meta_path.insert(0, VirtualPathFinder(storage))

# Звичайний імпорт віртуального модуля
import telemetry_client
response = telemetry_client.send_ping()
print("Результат віртуального виклику:", response)
