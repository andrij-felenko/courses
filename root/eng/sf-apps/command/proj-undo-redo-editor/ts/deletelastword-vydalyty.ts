class DeleteLastWord implements Command {
  private from = 0;         // звідки різали
  private removed = "";     // що саме зрізали (запам'ятаємо в execute)

  constructor(private doc: TextDocument) {}

  execute(): void {
    this.from = this.doc.lastWordStart();
    // remove повертає вирізане — ловимо його, поки воно не зникло назавжди
    this.removed = this.doc.remove(this.from, this.doc.length);
  }

  undo(): void {
    // повертаємо зрізане рівно туди, звідки взяли
    this.doc.insert(this.from, this.removed);
  }
}
