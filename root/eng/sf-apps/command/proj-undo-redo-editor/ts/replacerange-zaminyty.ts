class ReplaceRange implements Command {
  private oldText = "";     // що стояло в [from, to) до заміни

  constructor(
    private doc: TextDocument,
    private from: number,
    private to: number,
    private newText: string,
  ) {}

  execute(): void {
    // 1) вирізали старе — і одразу впіймали його в oldText
    this.oldText = this.doc.remove(this.from, this.to);
    // 2) вставили нове на те саме місце
    this.doc.insert(this.from, this.newText);
  }

  undo(): void {
    // дзеркально й у зворотному порядку:
    // 1) прибрати нове (воно завдовжки newText, стоїть від from)
    this.doc.remove(this.from, this.from + this.newText.length);
    // 2) повернути старе на місце
    this.doc.insert(this.from, this.oldText);
  }
}
