class Composite extends Component {
  add(child: Component): void {
    if (child === this || this.hasAncestor(child)) {
      throw new Error("додавання створило б цикл");   // гучна відмова, не тихе псування
    }
    child.parent?.remove(child);
    this.children.push(child);
    child.parent = this;
  }

  // чи є `candidate` десь на шляху від мене до кореня?
  private hasAncestor(candidate: Component): boolean {
    for (let p = this.parent; p !== null; p = p.parent) {
      if (p === candidate) return true;              // так — він мій пращур
    }
    return false;
  }
}
