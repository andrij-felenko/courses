# Python Implementation: Type-annotated BFS 2-coloring
from collections import deque
from typing import List, Optional, Tuple

def check_bipartite(n: int, edges: List[Tuple[int, int]]) -> Optional[List[int]]:
    """
    Перевіряє двочастковість графа з n вершинами (0..n-1).
    Повертає список кольорів [0, 1] для кожної вершини або None при наявності непарного циклу.
    """
    adj: List[List[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    colors = [-1] * n

    for start in range(n):
        if colors[start] != -1:
            continue

        colors[start] = 0
        queue = deque([start])

        while queue:
            u = queue.popleft()
            next_color = 1 - colors[u]

            for v in adj[u]:
                if colors[v] == -1:
                    colors[v] = next_color
                    queue.append(v)
                elif colors[v] == colors[u]:
                    return None  # Знайдено непарний цикл!

    return colors
