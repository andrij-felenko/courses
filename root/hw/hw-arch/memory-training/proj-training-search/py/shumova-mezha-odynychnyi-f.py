# Замазує «діри» з F завдовжки <= max_gap, оточені P з обох боків:
# такі короткі провали — шум на межі ока, а не справжній край.
# pf_map правиться на місці.
def despeckle(pf_map: list[bool], max_gap: int) -> None:
    n = len(pf_map)
    i = 0
    while i < n:
        if pf_map[i]:
            i += 1
            continue

        j = i                              # початок смуги F
        while j < n and not pf_map[j]:     # j — перша P після смуги (або n)
            j += 1
        gap = j - i                        # довжина смуги F

        bounded = (i > 0) and (j < n)      # P ліворуч І P праворуч
        if bounded and gap <= max_gap:
            for k in range(i, j):          # коротка внутрішня діра — затерти
                pf_map[k] = True
        i = j                              # йдемо далі від кінця смуги
