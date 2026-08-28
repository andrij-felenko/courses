class TreeNode {
  constructor(
    public key: number,
    public left: TreeNode | null = null,
    public right: TreeNode | null = null,
  ) {}
}

class BstInOrderIterator {
  private stack: TreeNode[] = [];

  constructor(root: TreeNode | null) {
    this.pushLeft(root);          // інваріант ставимо ще до першого next()
  }

  // заганяє вузол і весь його лівий хребет; вершиною стане найменший
  private pushLeft(node: TreeNode | null): void {
    while (node !== null) {
      this.stack.push(node);
      node = node.left;
    }
  }

  hasNext(): boolean {
    return this.stack.length > 0;   // порожній стек — обхід вичерпано
  }

  next(): number {
    const node = this.stack.pop()!; // вершина — найменший ще не відданий ключ
    this.pushLeft(node.right);      // тепер лівий хребет його правого піддерева
    return node.key;
  }
}
