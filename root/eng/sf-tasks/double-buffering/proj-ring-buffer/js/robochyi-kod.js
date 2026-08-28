const RB_SIZE = 256;                 // степінь двійки → швидка маска
const RB_MASK = RB_SIZE - 1;

class Ring {
  constructor() {
    this.buf = new Uint8Array(RB_SIZE);
    this.head = 0;                   // writer index
    this.tail = 0;                   // reader index
    this.count = 0;                  // зайнято байтів
  }

  // writer: true = записано, false = повно (політика «відкинути новий»)
  push(b) {
    if (this.count === RB_SIZE) return false;   // повно
    this.buf[this.head] = b;                     // 1) дані
    this.head = (this.head + 1) & RB_MASK;       // 2) посунути голову
    this.count++;
    return true;
  }

  // reader: повертає байт або null, якщо порожньо
  pop() {
    if (this.count === 0) return null;           // порожньо
    const b = this.buf[this.tail];
    this.tail = (this.tail + 1) & RB_MASK;
    this.count--;
    return b;
  }
}
