class TreeNode:
    def __init__(self, key, left=None, right=None):
        self.key = key
        self.left = left
        self.right = right


class BstInOrderIterator:
    def __init__(self, root):
        self._stack = []
        self._push_left(root)        # інваріант ставимо ще до першого next

    def _push_left(self, node):
        # заганяє вузол і весь його лівий хребет; вершиною стане найменший
        while node is not None:
            self._stack.append(node)
            node = node.left

    def has_next(self):
        return len(self._stack) > 0  # порожній стек — обхід вичерпано

    def __next__(self):
        node = self._stack.pop()     # вершина — найменший ще не відданий ключ
        self._push_left(node.right)  # тепер лівий хребет правого піддерева
        return node.key
