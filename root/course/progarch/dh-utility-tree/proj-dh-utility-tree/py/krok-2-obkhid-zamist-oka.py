def walk_leaves(node, path=()):
    """Обхід у глибину: усі листки, кожен — зі своїм ланцюгом гілок."""
    children = node.get("children")
    if children is None:                       # немає дітей → це листок
        yield {**node, "path": " › ".join(path)}
        return
    for child in children:
        yield from walk_leaves(child, path + (node["attribute"],))


def drivers(root):
    """Рівно ті листки, що (В, В): важливі І важкі."""
    leaves = (
        leaf
        for branch in root["children"]
        for leaf in walk_leaves(branch)
    )
    return [
        d for d in leaves
        if d["importance"] == "В" and d["difficulty"] == "В"
    ]


for d in drivers(tree):
    print(f'({d["importance"]},{d["difficulty"]})  {d["path"]}: {d["scenario"]}')
