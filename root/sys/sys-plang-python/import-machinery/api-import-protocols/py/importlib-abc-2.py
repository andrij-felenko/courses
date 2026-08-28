class importlib.abc.PathEntryFinder:
    def find_spec(
        self,
        fullname: str,
        target: types.ModuleType | None = None
    ) -> ModuleSpec | None:
        """Шукає специфікацію модуля в межах закріпленого каталогу/шляху."""
        ...

    def invalidate_caches(self) -> None:
        """Очищає кеш файлових дескрипторів або списків файлів каталогу."""
        ...
