class ExportRegistry:
    def __init__(self) -> None:
        self._by_ext: dict[str, Exporter] = {}

    def register(self, e: Exporter) -> None:   # сюди плагін кладе себе
        self._by_ext[e.extension] = e

    def export_as(self, ext: str, doc: "Document") -> bytes:
        e = self._by_ext.get(ext)              # ядро бере плагін за ключем
        if e is None:
            raise KeyError(f"немає плагіна для .{ext}")
        return e.export(doc)                    # і гукає через контракт
