_PARSERS: dict[str, Callable[[], ProfileParser]] = {}

def parses(*extensions: str):
    """Декоратор: реєструє клас-парсер під його розширеннями."""
    def wrap(cls):
        for ext in extensions:
            _PARSERS[ext] = cls
        return cls
    return wrap

@parses("json")
class JsonProfileParser:
    def parse(self, raw: str) -> "Profile": ...

@parses("yml", "yaml")             # два ключі на один клас — вільно
class YamlProfileParser:
    def parse(self, raw: str) -> "Profile": ...
