interface Order {
  readonly id: string;
  readonly items: string[];        // поле readonly, але сам масив — звичайний
}

const o: Order = { id: "A-1", items: ["cola"] };
o.items = [];                      // ✗ помилка: поле не перепризначити
o.items.push("beer");              // ✓ ДОЗВОЛЕНО — масив мінливий, гарантія протекла

interface SafeOrder {
  readonly id: string;
  readonly items: ReadonlyArray<string>;   // тепер і вміст лише для читання
}
