interface Command {
  execute(): void;
  undo(): void;
}

class DeleteLastWord implements Command {
  private removed = "";                 // сюди запам'ятаємо, що знесли
  constructor(private doc: Document) {}

  execute() {
    this.removed = this.doc.lastWord(); // запам'ятали ПЕРЕД руйнуванням
    this.doc.deleteLastWord();
  }
  undo() {
    this.doc.append(this.removed);      // повернули як було
  }
}
