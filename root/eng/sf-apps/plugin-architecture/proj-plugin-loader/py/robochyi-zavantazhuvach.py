import importlib.util
import logging
import sys
from pathlib import Path

from contract import HOST_API   # версія, яку вміє ЦЕ ядро

log = logging.getLogger("loader")


class ExportRegistry:
    """Серце ядра: сюди плагіни складають себе, звідси ядро їх бере."""
    def __init__(self) -> None:
        self._by_ext: dict[str, object] = {}

    def register(self, e) -> None:
        self._by_ext[e.extension] = e

    def export_as(self, ext: str, doc) -> bytes:
        return self._by_ext[ext].export(doc)


class Host:
    """Єдине вікно, яке ядро дає плагінові. Плагін дотягується до ядра
    ТІЛЬКИ через методи цього об'єкта — і нікуди більше."""
    def __init__(self, registry: ExportRegistry) -> None:
        self._registry = registry

    def register_exporter(self, e) -> None:
        # можна ще й перевірити тип e, щоб кривий плагін не поклав дурницю
        self._registry.register(e)
