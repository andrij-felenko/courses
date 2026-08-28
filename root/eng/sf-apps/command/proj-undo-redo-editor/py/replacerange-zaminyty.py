class ReplaceRange:
    def __init__(self, doc: TextDocument, frm: int, to: int, new_text: str) -> None:
        self.doc, self.frm, self.to, self.new_text = doc, frm, to, new_text
        self.old_text = ""    # що стояло в [from, to) до заміни

    def execute(self) -> None:
        # 1) вирізали старе — і одразу впіймали його в old_text
        self.old_text = self.doc.remove(self.frm, self.to)
        # 2) вставили нове на те саме місце
        self.doc.insert(self.frm, self.new_text)

    def undo(self) -> None:
        # дзеркально й у зворотному порядку:
        # 1) прибрати нове (воно завдовжки new_text, стоїть від from)
        self.doc.remove(self.frm, self.frm + len(self.new_text))
        # 2) повернути старе на місце
        self.doc.insert(self.frm, self.old_text)
