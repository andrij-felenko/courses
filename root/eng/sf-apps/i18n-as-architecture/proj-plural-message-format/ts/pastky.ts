function* choices(nodes: Node[]): Generator<Node> {
  for (const n of nodes)
    if (n.t === "choice") { yield n; for (const b of Object.values(n.branches)) yield* choices(b); }
}

function lint(catalog: Record<string, Record<string, string>>): string[] {
  const problems: string[] = [];
  for (const [lang, msgs] of Object.entries(catalog)) {
    const need = new Intl.PluralRules(lang).resolvedOptions().pluralCategories;
    for (const [key, pattern] of Object.entries(msgs))
      for (const node of choices(parse(pattern)))
        if (node.kind === "plural")
          for (const c of need)
            if (!(c in node.branches)) problems.push(`${lang}/${key}: бракує гілки «${c}»`);
  }
  return problems;
}

lint(catalog);   // [] — а без гілки few: ['uk/files.added: бракує гілки «few»']
