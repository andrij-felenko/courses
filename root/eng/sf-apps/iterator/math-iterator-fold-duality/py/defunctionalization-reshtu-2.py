class InOrderIterator:
    def __init__(self, root):
        self.stack = []
        self._descend(root)          # стан = стек напівпройдених вузлів

    def _descend(self, node):
        while node is not None:      # завантажуємо лівий хребет
            self.stack.append(node)
            node = node.left

    def has_next(self):
        return len(self.stack) > 0

    def next(self):
        node = self.stack.pop()      # δ: наступний найлівіший вузол
        self._descend(node.right)    # праве піддерево стає новою «рештою»
        return node.value
