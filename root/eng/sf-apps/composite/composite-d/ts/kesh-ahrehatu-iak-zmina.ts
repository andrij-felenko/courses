class Composite extends Component {
  private cached: number | null = null;   // збережений агрегат; null = брудний

  size(): number {
    if (this.cached === null) {            // брудний — рахуємо й запам'ятовуємо
      this.cached = this.children.reduce((s, c) => s + c.size(), 0);
    }
    return this.cached;                    // чистий — віддаємо миттєво, O(1)
  }

  invalidate(): void {                     // зробити брудним себе й усіх пращурів
    for (let p: Composite | null = this; p !== null; p = p.parent) {
      if (p.cached === null) break;        // уже брудний → вище теж брудні, спиняємось
      p.cached = null;
    }
  }

  add(child: Component): void {
    /* ...перевірки, вставка, parent... */
    this.children.push(child);
    child.parent = this;
    this.invalidate();                     // структура змінилась → шлях до кореня брудний
  }
}
