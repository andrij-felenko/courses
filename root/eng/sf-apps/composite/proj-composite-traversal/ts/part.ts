interface Component {
  readonly name: string;
}

class File implements Component {
  constructor(readonly name: string, readonly bytes: number) {}
}

class Folder implements Component {
  readonly children: Component[] = [];
  constructor(readonly name: string) {}

  add(c: Component): this {
    this.children.push(c);
    return this;                       // зручно ланцюжком будувати дерево
  }
}

// піддослідне дерево
const tree = new Folder("проєкт")
  .add(new Folder("src")
    .add(new File("main.ts", 1200))
    .add(new File("util.ts", 800))
    .add(new Folder("ui")
      .add(new File("button.ts", 640))
      .add(new File("modal.ts", 1500))))
  .add(new Folder("docs")
    .add(new File("guide.md", 300))
    .add(new File("api.md", 950)))
  .add(new File("README.md", 200));
