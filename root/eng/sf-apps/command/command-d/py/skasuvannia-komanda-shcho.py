class DeleteLastWord:
    def __init__(self, doc: Document) -> None:
        self.doc = doc
        self.removed = ""                # сюди запам'ятаємо, що знесли

    def execute(self) -> None:
        self.removed = self.doc.last_word()  # запам'ятали ПЕРЕД руйнуванням
        self.doc.delete_last_word()

    def undo(self) -> None:
        self.doc.append(self.removed)        # повернули як було
