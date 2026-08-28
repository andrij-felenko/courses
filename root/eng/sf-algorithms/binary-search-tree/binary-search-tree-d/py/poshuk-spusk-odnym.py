class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None

def find(t, key):
    while t:
        if key == t.key:
            return t                       # збіг
        t = t.left if key < t.key else t.right   # менший — ліворуч, більший — праворуч
    return None                            # впали з дерева — ключа немає
