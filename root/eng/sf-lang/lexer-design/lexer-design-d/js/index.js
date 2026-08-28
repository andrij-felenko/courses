const Kind = Object.freeze({
  NUM: "NUM", IDENT: "IDENT", PLUS: "PLUS", MINUS: "MINUS",
  STAR: "STAR", LPAREN: "LPAREN", RPAREN: "RPAREN", END: "END",
});

class Lexer {
  constructor(src) {
    this.src = src;
    this.pos = 0;                    // поточна позиція у вхідному тексті
  }

  #peek() {
    return this.pos < this.src.length ? this.src[this.pos] : "\0";
  }

  next() {
    while (/\s/.test(this.#peek())) this.pos++;   // 1) проковтнути пробіли

    if (this.#peek() === "\0")                    // кінець вводу
      return { kind: Kind.END };

    if (/[0-9]/.test(this.#peek())) {             // 2) НАЙДОВШЕ число
      let v = 0;
      while (/[0-9]/.test(this.#peek()))          // тягнемо цифри, доки йдуть
        v = v * 10 + (this.src.charCodeAt(this.pos++) - 48);  // рахуємо значення
      return { kind: Kind.NUM, value: v };
    }

    if (/[a-zA-Z]/.test(this.#peek())) {          // 3) НАЙДОВШЕ ім'я
      const start = this.pos;
      while (/[a-zA-Z0-9]/.test(this.#peek()))    // тягнемо буквоцифри
        this.pos++;
      return { kind: Kind.IDENT, text: this.src.slice(start, this.pos) }; // (ключові — нижче)
    }

    const singles = { "+": Kind.PLUS, "-": Kind.MINUS, "*": Kind.STAR,
                      "(": Kind.LPAREN, ")": Kind.RPAREN };
    const ch = this.src[this.pos++];              // 4) односимвольні оператори й дужки
    return { kind: singles[ch] ?? Kind.END };     // невідомий символ — тут спрощено
  }
}
