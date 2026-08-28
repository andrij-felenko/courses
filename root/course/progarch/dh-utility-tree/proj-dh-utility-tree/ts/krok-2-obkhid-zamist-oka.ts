interface Driver {
  path: string;         // ланцюг гілок від верху до листка = атрибут
  scenario: string;
  measure: string;
  importance: Grade;
  difficulty: Grade;
}

// Обхід у глибину: зносимо всі листки в один плаский список,
// несучи з собою ланцюг гілок над кожним листком.
function* walkLeaves(node: Node, path: string[] = []): Generator<Driver> {
  if (node.kind === "leaf") {
    yield {
      path: path.join(" › "),
      scenario: node.scenario,
      measure: node.measure,
      importance: node.importance,
      difficulty: node.difficulty,
    };
    return;
  }
  for (const child of node.children) {
    yield* walkLeaves(child, [...path, node.attribute]);
  }
}

// Драйвери — рівно ті листки, що (В, В): важливі І важкі.
function drivers(root: Branch): Driver[] {
  return root.children
    .flatMap((branch) => [...walkLeaves(branch)])
    .filter((d) => d.importance === "В" && d.difficulty === "В");
}

for (const d of drivers(tree)) {
  console.log(`(${d.importance},${d.difficulty})  ${d.path}: ${d.scenario}`);
}
