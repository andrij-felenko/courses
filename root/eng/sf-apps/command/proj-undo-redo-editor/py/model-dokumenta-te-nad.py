class TextDocument:
    def __init__(self) -> None:
        self._text = ""

    def content(self) -> str:
        return self._text

    def __len__(self) -> int:
        return len(self._text)

    # вставити рядок у позицію pos (0 ≤ pos ≤ len)
    def insert(self, pos: int, s: str) -> None:
        self._text = self._text[:pos] + s + self._text[pos:]

    # вирізати [from, to) і повернути вирізане (щоб команда його запам'ятала)
    def remove(self, frm: int, to: int) -> str:
        cut = self._text[frm:to]
        self._text = self._text[:frm] + self._text[to:]
        return cut

    # межа останнього слова: індекс, з якого воно починається
    def last_word_start(self) -> int:
        trimmed_end = len(self._text.rstrip())    # без хвостових пробілів
        sp = self._text.rfind(" ", 0, trimmed_end)
        return sp + 1                             # -1 → 0 (слово від початку)
