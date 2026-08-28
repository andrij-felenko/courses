# рекурсивно: системний стек веде облік за нас
def tree_sum(node):
    total = node.value
    for child in node.children:
        total += tree_sum(child)
    return total

# ітеративно: стек ведемо ми — звичайним масивом
def tree_sum_iter(root):
    total = 0
    stack = [root]                   # ще-не-оброблені вузли
    while stack:                     # поки є що обробляти
        node = stack.pop()           # знімаємо один
        total += node.value
        for child in node.children:
            stack.append(child)      # дітей — у стек, на потім
    return total
