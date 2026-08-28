// рекурсивно: системний стек веде облік за нас
function treeSum(node) {
  let total = node.value;
  for (const child of node.children) total += treeSum(child);
  return total;
}

// ітеративно: стек ведемо ми — звичайним масивом
function treeSumIter(root) {
  let total = 0;
  const stack = [root];              // ще-не-оброблені вузли
  while (stack.length) {             // поки є що обробляти
    const node = stack.pop();        // знімаємо один
    total += node.value;
    for (const child of node.children) stack.push(child); // на потім
  }
  return total;
}
