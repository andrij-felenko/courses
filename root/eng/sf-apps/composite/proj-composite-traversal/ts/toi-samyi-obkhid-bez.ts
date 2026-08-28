function countNodesIter(root: Component): number {
  let total = 0;
  const stack: Component[] = [root];       // наш власний стек — у купі
  while (stack.length > 0) {
    const node = stack.pop()!;             // беремо вузол на обробку
    total++;                               // рахуємо його
    if (node instanceof Folder) {
      for (const child of node.children) {
        stack.push(child);                 // дітей — назад у стек, на потім
      }
    }
  }
  return total;
}

console.log(countNodesIter(tree));   // 10
