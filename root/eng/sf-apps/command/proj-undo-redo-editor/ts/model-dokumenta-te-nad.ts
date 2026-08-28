class TextDocument {
  private text = "";

  content(): string { return this.text; }
  get length(): number { return this.text.length; }

  // вставити рядок у позицію pos (0 ≤ pos ≤ length)
  insert(pos: number, s: string): void {
    this.text = this.text.slice(0, pos) + s + this.text.slice(pos);
  }

  // вирізати [from, to) і повернути вирізане (щоб команда його запам'ятала)
  remove(from: number, to: number): string {
    const cut = this.text.slice(from, to);
    this.text = this.text.slice(0, from) + this.text.slice(to);
    return cut;
  }

  // межа останнього слова: індекс, з якого воно починається
  lastWordStart(): number {
    const trimmedEnd = this.text.replace(/\s+$/, "").length; // без хвостових пробілів
    const sp = this.text.lastIndexOf(" ", trimmedEnd - 1);
    return sp + 1;                       // -1 → 0 (слово від початку)
  }
}
