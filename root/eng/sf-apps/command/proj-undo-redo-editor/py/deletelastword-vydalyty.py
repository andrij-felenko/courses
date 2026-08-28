class DeleteLastWord:
    def __init__(self, doc: TextDocument) -> None:
        self.doc = doc
        self.frm = 0          # звідки різали
        self.removed = ""     # що саме зрізали (запам'ятаємо в execute)

    def execute(self) -> None:
        self.frm = self.doc.last_word_start()
        # remove повертає вирізане — ловимо його, поки воно не зникло назавжди
        self.removed = self.doc.remove(self.frm, len(self.doc))

    def undo(self) -> None:
        # повертаємо зрізане рівно туди, звідки взяли
        self.doc.insert(self.frm, self.removed)
