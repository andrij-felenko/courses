from abc import ABC, abstractmethod

class Importer(ABC):
    # ШАБЛОННИЙ МЕТОД: каркас; нащадки його не перевизначають
    def import_file(self, path: str) -> None:
        text = self._read_file(path)                       # спільний крок
        rows = [r for r in self.parse(text) if self.is_valid(r)]  # дірка + гачок
        self._save_all(rows)                               # спільний крок
        self._log(len(rows))                               # спільний крок

    @abstractmethod
    def parse(self, text: str) -> list["Record"]: ...      # мусить дати нащадок

    def is_valid(self, r: "Record") -> bool:               # гачок із типовим «так»
        return True

    def _read_file(self, path): ...     # однакове для всіх
    def _save_all(self, rows): ...      # однакове для всіх
    def _log(self, n): ...              # однакове для всіх

class CsvImporter(Importer):
    def parse(self, text): ...          # комами

class JsonImporter(Importer):
    def parse(self, text): ...          # JSON
    def is_valid(self, r):              # суворіше
        return r.id > 0
