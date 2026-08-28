def eval_tree(root):
    stack = [(root, False)]              # False = діти ще не розкриті
    ready = []                           # готові значення піддерев
    while stack:
        node, expanded = stack.pop()
        if node.is_leaf():
            ready.append(node.value)
        elif not expanded:
            stack.append((node, True))   # повернемось ПІСЛЯ дітей
            stack.append((node.right, False))
            stack.append((node.left, False))   # лівий згори — вийметься першим
        else:                            # діти вже пораховані — беремо їхні значення
            b = ready.pop(); a = ready.pop()
            ready.append(apply(node.op, a, b))
    return ready.pop()
