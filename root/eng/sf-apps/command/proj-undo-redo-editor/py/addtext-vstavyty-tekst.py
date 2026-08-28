class AddText:
    def __init__(self, doc: TextDocument, pos: int, text: str) -> None:
        self.doc, self.pos, self.text = doc, pos, text

    def execute(self) -> None:
        self.doc.insert(self.pos, self.text)

    def undo(self) -> None:
        # вставили text у pos → щоб відкотити, вирізаємо [pos, pos + len(text))
        self.doc.remove(self.pos, self.pos + len(self.text))
