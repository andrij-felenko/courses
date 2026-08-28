def closure(gens, op):
    """Замкнути твірні за операцією op — уся породжена група."""
    G = set(gens)
    frontier = list(gens)          # елементи, ще не перемножені з усіма
    while frontier:
        fresh = []
        for a in list(G):
            for b in frontier:
                for x in (op(a, b), op(b, a)):
                    if x not in G:
                        G.add(x)
                        fresh.append(x)
        frontier = fresh
    return G
