from dataclasses import dataclass
from typing import Optional, Any

@dataclass(frozen=True)            # frozen — поля вузла вже не переприсвоїш: він незмінний
class Node:
    key:   Any
    val:   Any
    left:  Optional["Node"]
    right: Optional["Node"]

def insert(node: Optional[Node], key, val) -> Node:
    if node is None:                                       # дійшли до порожнього місця —
        return Node(key, val, None, None)                 #   новий листок

    if key < node.key:                                    # ліворуч: новий вузол,
        return Node(node.key, node.val,                   #   той самий ключ і значення,
                    insert(node.left, key, val),          #   НОВЕ ліве (рекурсія),
                    node.right)                           #   СПІЛЬНЕ праве (той самий об'єкт)

    if key > node.key:                                    # праворуч: дзеркально
        return Node(node.key, node.val,
                    node.left,                            #   СПІЛЬНЕ ліве
                    insert(node.right, key, val))         #   НОВЕ праве

    return Node(key, val, node.left, node.right)          # ключ уже є — нове значення,
                                                          #   обидві дитини спільні (оновлення)
