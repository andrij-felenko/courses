abstract class Component {
  abstract size(): number;
  getComposite(): Composite | null { return null; }   // лист за замовчуванням — не композит
}

class Leaf extends Component {
  constructor(private bytes: number) { super(); }
  size(): number { return this.bytes; }
  // getComposite() успадкований → null: лист чесно зізнається, що дітей не має
}

class Composite extends Component {
  readonly children: Component[] = [];
  size(): number { return this.children.reduce((s, c) => s + c.size(), 0); }
  getComposite(): Composite { return this; }           // лише композит віддає себе
  add(child: Component): void { /* ... */ }
}

// клієнт: одне питання замість розсипу instanceof
function tryAdd(node: Component, child: Component): void {
  const box = node.getComposite();
  if (box !== null) {
    box.add(child);          // тип звужено до Composite статично — add доступний і безпечний
  }
  // якщо null — це лист, додавати нема куди, і ми це знаємо чесно
}
