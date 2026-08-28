function countNodes(node: Component): number {
  if (node instanceof Folder) {
    let total = 1;                         // сама тека — один вузол
    for (const child of node.children) {
      total += countNodes(child);          // плюс усе, що в кожній дитині
    }
    return total;
  }
  return 1;                                // листок — рівно один вузол
}

console.log(countNodes(tree));   // 10
