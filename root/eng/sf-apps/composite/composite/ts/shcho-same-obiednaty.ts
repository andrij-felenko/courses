interface Component {
  size(): number;                 // спільний інтерфейс: обіцянка обом
}

class File implements Component {
  constructor(private bytes: number) {}
  size(): number {
    return this.bytes;            // лист: власне число
  }
}

class Folder implements Component {
  private children: Component[] = [];

  add(c: Component): void {        // тільки в компонувальника
    this.children.push(c);
  }

  size(): number {
    let sum = 0;
    for (const c of this.children) {
      sum += c.size();            // питаю розмір, НЕ питаючи, хто це
    }
    return sum;
  }
}
