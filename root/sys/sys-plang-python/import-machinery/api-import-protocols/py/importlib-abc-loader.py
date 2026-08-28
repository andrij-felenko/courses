class importlib.abc.Loader:
    def create_module(self, spec: ModuleSpec) -> types.ModuleType | None:
        """Алокує новий об'єкт модуля.
        
        Повертає новий types.ModuleType або None. Якщо повернено None,
        CPython створює стандартний модуль types.ModuleType(spec.name).
        """
        return None

    def exec_module(self, module: types.ModuleType) -> None:
        """Виконує код модуля у просторі імен module.__dict__.
        
        Обов'язковий метод за стандартом PEP 451. Усі винятки,
        викинуті цим методом, призводять до відкату та видалення
        модуля з sys.modules.
        """
        ...

    def load_module(self, fullname: str) -> types.ModuleType:
        """Застарілий метод епохи PEP 302.
        
        У сучасному коді не реалізується; за замовчуванням емулюється
        через виклики create_module() та exec_module().
        """
        ...
