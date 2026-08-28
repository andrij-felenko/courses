def count_nodes(node: Component) -> int:
    if isinstance(node, Folder):
        total = 1                          # сама тека — один вузол
        for child in node.children:
            total += count_nodes(child)    # плюс усе, що в кожній дитині
        return total
    return 1                               # листок — рівно один вузол


print(count_nodes(tree))   # 10
