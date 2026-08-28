from typing import Callable

# реєстр: ключ → конструктор. Відповідність стала ДАНИМИ, а не гілками коду
_PARSERS: dict[str, Callable[[], ProfileParser]] = {
    "json": JsonProfileParser,
    "csv":  CsvProfileParser,
    "xml":  XmlProfileParser,
}

def parser_for_file(path: str) -> ProfileParser:
    ext = path.rsplit(".", 1)[-1].lower()
    try:
        ctor = _PARSERS[ext]
    except KeyError:
        raise ValueError(f"Немає парсера для формату .{ext}") from None
    return ctor()

# новий формат — БЕЗ дотику до parser_for_file: лише запис у таблицю
def register_parser(ext: str, ctor: Callable[[], ProfileParser]) -> None:
    _PARSERS[ext] = ctor
