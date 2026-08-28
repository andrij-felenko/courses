function collectByLevel(root: Component): string[] {
  const out: string[] = [];
  const queue: Component[] = [root];       // черга замість стека — обхід ушир
  while (queue.length > 0) {
    const node = queue.shift()!;           // беремо з ПОЧАТКУ (FIFO)
    out.push(node.name);
    if (node instanceof Folder) {
      for (const child of node.children) {
        queue.push(child);                 // діти йдуть у хвіст
      }
    }
  }
  return out;   // [проєкт, src, docs, README.md, main.ts, util.ts, ui, ...]
}
