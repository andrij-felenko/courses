def count_nodes_iter(root: Component) -> int:
    total = 0
    stack: list[Component] = [root]        # наш власний стек — у купі
    while stack:
        node = stack.pop()                 # беремо вузол на обробку
        total += 1                         # рахуємо його
        if isinstance(node, Folder):
            stack.extend(node.children)    # дітей — назад у стек, на потім
    return total


print(count_nodes_iter(tree))   # 10
