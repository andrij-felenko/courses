def min_node(t):
    while t.left:
        t = t.left
    return t

def erase(t, key):
    if t is None:
        return None
    if key < t.key:
        t.left = erase(t.left, key)
    elif key > t.key:
        t.right = erase(t.right, key)
    else:                                  # знайшли вузол
        if t.left is None:
            return t.right                 # 0 або 1 дитина
        if t.right is None:
            return t.left
        s = min_node(t.right)              # наступник
        t.key = s.key                      # переносимо ключ
        t.right = erase(t.right, s.key)    # видаляємо наступника
    return t
