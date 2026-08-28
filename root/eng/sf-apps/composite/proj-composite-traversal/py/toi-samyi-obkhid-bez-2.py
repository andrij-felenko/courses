from collections import deque

def collect_by_level(root: Component) -> list[str]:
    out: list[str] = []
    queue = deque([root])                  # черга замість стека — обхід ушир
    while queue:
        node = queue.popleft()             # беремо з ПОЧАТКУ (FIFO)
        out.append(node.name)
        if isinstance(node, Folder):
            queue.extend(node.children)    # діти йдуть у хвіст
    return out   # [проєкт, src, docs, README.md, main.ts, util.ts, ui, ...]
