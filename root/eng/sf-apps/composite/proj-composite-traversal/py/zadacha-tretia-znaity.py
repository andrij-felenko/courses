def largest_file(node: Component) -> File | None:
    if isinstance(node, File):
        return node                        # листок сам собі чемпіон

    best: File | None = None
    for child in node.children:
        candidate = largest_file(child)    # чемпіон піддерева-дитини
        if candidate and (best is None or candidate.num_bytes > best.num_bytes):
            best = candidate
    return best                            # порожня тека поверне None


top = largest_file(tree)
print(top.name, top.num_bytes if top else None)   # modal.ts 1500
