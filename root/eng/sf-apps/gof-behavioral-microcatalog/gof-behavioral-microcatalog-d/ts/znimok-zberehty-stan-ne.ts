// Знімок — непрозора коробка. Доглядач може її ТРИМАТИ,
// але поля читає лише сам редактор, що її створив.
class EditorMemento {
  constructor(
    readonly text: string,       // readonly: знімок — фотографія, не жива змінна
    readonly cursor: number,
  ) {}
}

class Editor {                    // Джерело
  private text = "";
  private cursor = 0;

  type(s: string) {
    this.text = this.text.slice(0, this.cursor) + s + this.text.slice(this.cursor);
    this.cursor += s.length;
  }

  save(): EditorMemento {         // САМЕ пакує свій стан у коробку
    return new EditorMemento(this.text, this.cursor);
  }
  restore(m: EditorMemento) {     // і САМЕ вміє з неї відновитися
    this.text = m.text;
    this.cursor = m.cursor;
  }
  toString() { return this.text; }
}

// Доглядач — стос скасувань: тримає коробки, всередину не заглядає
const editor = new Editor();
const history: EditorMemento[] = [];

editor.type("Привіт");
history.push(editor.save());      // контрольна точка
editor.type(", світе");
console.log(`${editor}`);          // "Привіт, світе"

editor.restore(history.pop()!);   // undo
console.log(`${editor}`);          // "Привіт"
