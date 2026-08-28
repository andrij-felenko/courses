abstract class Component {
  abstract size(): number;

  // прозорість: методи є в кожного, але за замовчуванням чесно відмовляють
  add(c: Component): void {
    throw new Error("листок не може мати дітей");
  }
  remove(c: Component): void {
    throw new Error("листок не може мати дітей");
  }
}

class File extends Component {
  constructor(private bytes: number) { super(); }
  size(): number { return this.bytes; }
  // add/remove успадковані — кинуть виняток, і це чесно
}

class Folder extends Component {
  private children: Component[] = [];
  size(): number { return this.children.reduce((s, c) => s + c.size(), 0); }
  add(c: Component): void { this.children.push(c); }        // перевизначає
  remove(c: Component): void {
    this.children = this.children.filter(x => x !== c);
  }
}
