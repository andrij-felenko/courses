// вузол — розрізнюване об'єднання: рівно одна з форм
type Node =
  | { kind: "leaf"; bytes: number }
  | { kind: "composite"; children: Node[] };

// операція — вільна функція; switch розбирає форми
function size(node: Node): number {
  switch (node.kind) {
    case "leaf":      return node.bytes;
    case "composite": return node.children.reduce((s, c) => s + size(c), 0);
  }
}

// ДОДАТИ ОПЕРАЦІЮ — нова функція, наявне незаймане:
function count(node: Node): number {
  switch (node.kind) {
    case "leaf":      return 1;
    case "composite": return 1 + node.children.reduce((s, c) => s + count(c), 0);
  }
}
