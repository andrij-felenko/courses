from typing import Protocol

class ProfileParser(Protocol):
    def parse(self, raw: str) -> "Profile": ...

class JsonProfileParser: 
    def parse(self, raw: str) -> "Profile": ...   # ...
class CsvProfileParser:
    def parse(self, raw: str) -> "Profile": ...
class XmlProfileParser:
    def parse(self, raw: str) -> "Profile": ...

# параметризований фабричний метод: за КЛЮЧЕМ (розширення) обирає клас
def parser_for_file(path: str) -> ProfileParser:
    ext = path.rsplit(".", 1)[-1].lower()
    if ext == "json":
        return JsonProfileParser()
    if ext == "csv":
        return CsvProfileParser()
    if ext == "xml":
        return XmlProfileParser()
    raise ValueError(f"Немає парсера для формату .{ext}")
