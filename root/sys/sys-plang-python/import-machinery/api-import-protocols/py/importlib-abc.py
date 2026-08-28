class importlib.abc.MetaPathFinder:
    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None,
        target: types.ModuleType | None = None
    ) -> ModuleSpec | None:
        """Шукає специфікацію модуля.
        
        Параметри:
          fullname: повна кваліфікована назва модуля.
          path: None для модулів верхнього рівня або значення __path__ 
                батьківського пакунка при імпорті підмодуля.
          target: існуючий модуль (передається лише під час перезавантаження reload()).
        """
        ...

    def invalidate_caches(self) -> None:
        """Скидає внутрішні кеші знахідника (викликається importlib.invalidate_caches())."""
        ...
