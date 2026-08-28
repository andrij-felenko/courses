function largestFile(node: Component): File | null {
  if (node instanceof File) return node;   // листок сам собі чемпіон

  let best: File | null = null;
  for (const child of node.children) {
    const candidate = largestFile(child);   // чемпіон піддерева-дитини
    if (candidate && (!best || candidate.bytes > best.bytes)) {
      best = candidate;
    }
  }
  return best;                              // порожня тека поверне null
}

const top = largestFile(tree);
console.log(top?.name, top?.bytes);   // modal.ts 1500
