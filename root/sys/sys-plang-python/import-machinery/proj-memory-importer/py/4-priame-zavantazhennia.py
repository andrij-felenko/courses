import marshal
import types


class BytecodeInMemoryLoader(InMemoryLoader):
    """Високошвидкісний завантажувач сирого байткоду з пам'яті."""

    def __init__(self, raw_bytecode: bytes, is_package: bool = False):
        super().__init__(source_code="", is_package=is_package)
        self.raw_bytecode = raw_bytecode

    def exec_module(self, module: types.ModuleType) -> None:
        # Десеріалізація об'єкта PyCodeObject з бінарного рядка
        code_object = marshal.loads(self.raw_bytecode)
        
        # Виконання десеріалізованого байткоду
        exec(code_object, module.__dict__)
