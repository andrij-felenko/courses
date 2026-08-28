interface Command {
  execute(): void;
}

class AddText implements Command {
  constructor(private doc: Document, private text: string) {}
  execute() { this.doc.insert(this.text); }   // знання «що робити» живе ТУТ
}

class DeleteLast implements Command {
  constructor(private doc: Document) {}
  execute() { this.doc.deleteLast(); }
}
