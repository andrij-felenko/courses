interface DocBuilder {              // РОЛІ кроків — те, ЩО можна робити
  addHeader(text: string): void;
  addParagraph(text: string): void;
  getResult(): string;
}

class HtmlBuilder implements DocBuilder {     // одне представлення — HTML
  private out = "";
  addHeader(t: string)    { this.out += `<h1>${t}</h1>\n`; }
  addParagraph(t: string) { this.out += `<p>${t}</p>\n`; }
  getResult()             { return this.out; }
}

class PlainBuilder implements DocBuilder {    // інше представлення — текст
  private out = "";
  addHeader(t: string)    { this.out += t.toUpperCase() + "\n"; }
  addParagraph(t: string) { this.out += t + "\n"; }
  getResult()             { return this.out; }
}

class Director {                    // знає лише ПОРЯДОК, не знає матеріалу
  build(b: DocBuilder): void {
    b.addHeader("Звіт");
    b.addParagraph("Перший абзац.");
    b.addParagraph("Другий абзац.");
  }
}

const director = new Director();
const html = new HtmlBuilder();
director.build(html);              // той самий обхід...
console.log(html.getResult());     // ...дав HTML

const plain = new PlainBuilder();
director.build(plain);             // ...той самий обхід...
console.log(plain.getResult());    // ...дав звичайний текст
