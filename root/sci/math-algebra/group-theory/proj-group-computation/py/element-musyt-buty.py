def pmul(g, h):                 # g після h:  (g·h)[i] = g[h[i]]
    return tuple(g[h[i]] for i in range(len(g)))

def pinv(g):                    # обернена перестановка
    inv = [0] * len(g)
    for i, gi in enumerate(g):
        inv[gi] = i
    return tuple(inv)

e3 = (0, 1, 2)                  # тотожність
r  = (1, 2, 0)                  # поворот  0→1→2→0
s1 = (0, 2, 1)                  # відбиття, що лишає вершину 0 на місці
