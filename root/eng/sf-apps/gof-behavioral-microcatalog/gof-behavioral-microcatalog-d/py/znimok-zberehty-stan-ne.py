from dataclasses import dataclass

# frozen=True: знімок незмінний — справжня фотографія, а не посилання на живий стан
@dataclass(frozen=True)
class EditorMemento:
    text: str
    cursor: int

class Editor:                     # Джерело
    def __init__(self):
        self._text = ""
        self._cursor = 0

    def type(self, s: str) -> None:
        self._text = self._text[:self._cursor] + s + self._text[self._cursor:]
        self._cursor += len(s)

    def save(self) -> EditorMemento:          # САМЕ пакує свій стан
        return EditorMemento(self._text, self._cursor)

    def restore(self, m: EditorMemento) -> None:   # і САМЕ з нього відновлюється
        self._text, self._cursor = m.text, m.cursor

    def __str__(self) -> str:
        return self._text

# Доглядач — стос скасувань: тримає знімки, всередину не заглядає
editor = Editor()
history: list[EditorMemento] = []

editor.type("Привіт")
history.append(editor.save())     # контрольна точка
editor.type(", світе")
print(editor)                      # Привіт, світе

editor.restore(history.pop())     # undo
print(editor)                      # Привіт
