function collectPaths(
  node: Component,
  prefix = "",
  out: string[] = [],
): string[] {
  const path = prefix ? `${prefix}/${node.name}` : node.name;
  if (node instanceof Folder) {
    for (const child of node.children) {
      collectPaths(child, path, out);      // спускаємось, несучи шлях сюди
    }
  } else {
    out.push(path);                        // листок — фіксуємо повний шлях
  }
  return out;
}

for (const p of collectPaths(tree)) console.log(p);
// проєкт/src/main.ts
// проєкт/src/util.ts
// проєкт/src/ui/button.ts
// проєкт/src/ui/modal.ts
// проєкт/docs/guide.md
// проєкт/docs/api.md
// проєкт/README.md
