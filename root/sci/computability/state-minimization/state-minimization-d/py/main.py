def minimize(states, alphabet, delta, accept):
    # delta[s][a] -> наступний стан;  accept — множина приймальних станів
    # стартове розбиття: приймальні (1) окремо від решти (0)
    part = {s: (1 if s in accept else 0) for s in states}
    while True:
        # підпис = (свій блок, блоки, куди ведуть переходи по кожному символу)
        sig = {s: (part[s], tuple(part[delta[s][a]] for a in alphabet))
               for s in states}
        # однакові підписи -> той самий новий блок
        ids = {v: i for i, v in enumerate(sorted(set(sig.values())))}
        new_part = {s: ids[sig[s]] for s in states}
        if new_part == part:          # ніщо не розкололось цього проходу — готово
            return new_part           # {стан: номер класу}
        part = new_part
