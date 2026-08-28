from abc import ABC, abstractmethod

class Application(ABC):
    @abstractmethod
    def create_document(self) -> "Document":   # фабричний метод: діра для нащадка
        ...

    def new_document(self) -> "Document":      # спільна логіка каркаса
        doc = self.create_document()           # ...кличе діру...
        doc.open()
        self._register_in_recent(doc)
        return doc

    def _register_in_recent(self, doc: "Document") -> None:
        ...

class DrawingApp(Application):
    def create_document(self) -> "Document":   # нащадок ОБИРАЄ клас
        return DrawingDocument()

class SpreadsheetApp(Application):
    def create_document(self) -> "Document":
        return SpreadsheetDocument()
