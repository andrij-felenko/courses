from typing import Protocol

class Command(Protocol):
    def execute(self) -> None: ...

class AddText:
    def __init__(self, doc: Document, text: str) -> None:
        self.doc, self.text = doc, text
    def execute(self) -> None:
        self.doc.insert(self.text)          # знання «що робити» живе ТУТ

class DeleteLast:
    def __init__(self, doc: Document) -> None:
        self.doc = doc
    def execute(self) -> None:
        self.doc.delete_last()
