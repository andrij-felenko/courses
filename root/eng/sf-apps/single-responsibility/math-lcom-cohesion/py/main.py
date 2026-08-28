from itertools import combinations

def lcom_components(methods, calls=()):
    # methods: словник  ім'я → множина полів, яких метод торкається
    # calls:   пари (a, b) — метод a кличе метод b
    parent = {m: m for m in methods}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]   # стиснення шляху
            x = parent[x]
        return x

    def union(a, b):
        parent[find(a)] = find(b)

    for a, b in combinations(methods, 2):
        if methods[a] & methods[b]:         # ребро: спільне поле
            union(a, b)
    for a, b in calls:                      # ребро: виклик
        union(a, b)

    return len({find(m) for m in methods})  # скільки різних коренів — стільки компонент
