from collections import deque

# adj[v] — список сусідів вершини v; вершини занумеровано 0..N-1
def reachable(adj, src, dst):
    if src == dst:
        return True
    seen = [False] * len(adj)            # хто вже відвіданий
    frontier = deque([src])              # фронт хвилі обходу
    seen[src] = True

    while frontier:
        v = frontier.popleft()
        for nb in adj[v]:                # усі сусіди поточної вершини
            if nb == dst:                # дійшли до цілі
                return True
            if not seen[nb]:             # ще не бачили — у фронт
                seen[nb] = True
                frontier.append(nb)
    return False                         # фронт вичерпано — шляху нема
