abstract class Component {
  parent: Composite | null = null;      // зворотне посилання вгору; у кореня — null
  abstract size(): number;
}

class Leaf extends Component {
  constructor(private bytes: number) { super(); }
  size(): number { return this.bytes; }
}

class Composite extends Component {
  readonly children: Component[] = [];

  add(child: Component): void {
    child.parent?.remove(child);        // спершу від'єднати від старого батька
    this.children.push(child);          // 1) додали в список (зв'язок униз)
    child.parent = this;                // 2) той самий крок ставить .parent (зв'язок угору)
  }

  remove(child: Component): void {
    const i = this.children.indexOf(child);
    if (i >= 0) {
      this.children.splice(i, 1);       // прибрали зі списку
      child.parent = null;              // і одразу обнулили батька
    }
  }

  size(): number {
    return this.children.reduce((sum, c) => sum + c.size(), 0);
  }
}
