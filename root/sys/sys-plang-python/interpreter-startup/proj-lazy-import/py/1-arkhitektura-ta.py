import sys
import time
import types
import threading
import importlib
import importlib.util
from typing import Any, Dict, List


class LazyModuleProxy(types.ModuleType):
    """
    Потокобезпечний проксі-модуль, який відкладає зчитування та виконання коду
    до моменту першого звернення до будь-якого атрибута.
    """

    def __init__(self, module_name: str, package: str | None = None):
        super().__init__(module_name)
        # Використовуємо прямий запис у __dict__, щоб уникнути виклику __setattr__
        self.__dict__["_lazy_module_name"] = module_name
        self.__dict__["_lazy_package"] = package
        self.__dict__["_real_module"] = None
        self.__dict__["_lock"] = threading.Lock()

    def _resolve_module(self) -> types.ModuleType:
        """Виконує фактичний імпорт модуля з блокуванням стану гонитви."""
        # Швидка перевірка без взяття блокування (First Check)
        real = self.__dict__.get("_real_module")
        if real is not None:
            return real

        lock: threading.Lock = self.__dict__["_lock"]
        with lock:
            # Повторна перевірка після отримання блокування (Second Check)
            real = self.__dict__.get("_real_module")
            if real is not None:
                return real

            name: str = self.__dict__["_lazy_module_name"]
            pkg: str | None = self.__dict__["_lazy_package"]

            # Фактичний імпорт через стандартний механізм CPython
            real = importlib.import_module(name, package=pkg)
            self.__dict__["_real_module"] = real

            # Оновлюємо системний словник завантажених модулів
            sys.modules[name] = real
            return real

    def __getattr__(self, item: str) -> Any:
        real = self._resolve_module()
        return getattr(real, item)

    def __setattr__(self, key: str, value: Any) -> None:
        if key in ("_lazy_module_name", "_lazy_package", "_real_module", "_lock"):
            super().__setattr__(key, value)
            return
        real = self._resolve_module()
        setattr(real, key, value)

    def __dir__(self) -> List[str]:
        real = self._resolve_module()
        return dir(real)

    def __repr__(self) -> str:
        real = self.__dict__.get("_real_module")
        state = "loaded" if real is not None else "deferred"
        return f"<LazyModuleProxy '{self.__dict__['_lazy_module_name']}' ({state})>"


def lazy_import(name: str, package: str | None = None) -> types.ModuleType:
    """
    Фабрика для створення екземпляра відкладеного модуля.
    """
    proxy = LazyModuleProxy(name, package)
    return proxy
