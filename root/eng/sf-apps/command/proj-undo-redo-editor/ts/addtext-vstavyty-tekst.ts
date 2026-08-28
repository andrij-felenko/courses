class AddText implements Command {
  constructor(
    private doc: TextDocument,
    private pos: number,
    private text: string,
  ) {}

  execute(): void {
    this.doc.insert(this.pos, this.text);
  }

  undo(): void {
    // вставили text у pos → щоб відкотити, вирізаємо [pos, pos + text.length)
    this.doc.remove(this.pos, this.pos + this.text.length);
  }
}
