def subcells(gaps):
    """Пороги (еВ) → фотострум кожного піделемента, мА/см².
    Фотон ловить НАЙВИЩИЙ поріг, який переступає:
    піделемент з порогом Eg_i збирає смугу [Eg_i, Eg_{i−1})."""
    g = sorted(gaps, reverse=True)          # згори (широка зона) вниз
    edges = [4.0] + g                       # 4.0 еВ — верх табульованого спектра
    return [photocurrent(edges[i+1], edges[i]) for i in range(len(g))]

def stack(gaps):
    "Струм стосу = найслабший піделемент; решта — надлишок у тепло."
    J = subcells(gaps)
    Jstack = min(J)
    excess = [round(j - Jstack, 1) for j in J]
    return round(Jstack, 1), [round(j, 1) for j in J], excess
