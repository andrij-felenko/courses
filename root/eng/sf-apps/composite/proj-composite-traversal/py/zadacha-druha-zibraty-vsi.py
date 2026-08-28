def collect_paths(
    node: Component,
    prefix: str = "",
    out: list[str] | None = None,
) -> list[str]:
    if out is None:
        out = []                           # не роби [] значенням за замовчуванням!
    path = f"{prefix}/{node.name}" if prefix else node.name
    if isinstance(node, Folder):
        for child in node.children:
            collect_paths(child, path, out)   # спускаємось, несучи шлях сюди
    else:
        out.append(path)                   # листок — фіксуємо повний шлях
    return out


for p in collect_paths(tree):
    print(p)
