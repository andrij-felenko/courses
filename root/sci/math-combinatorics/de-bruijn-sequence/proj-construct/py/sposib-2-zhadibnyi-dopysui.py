def de_bruijn_greedy(k, n):
    seq = [0] * n                          # старт: n нулів
    seen = {tuple(seq)}                    # єдине поки що вікно
    while True:
        tail = tuple(seq[len(seq) - (n - 1):])       # останні n-1 символів
        c = next((s for s in range(k - 1, -1, -1)    # найбільший символ,
                  if tail + (s,) not in seen), None)  # що не повторює вікна
        if c is None:                      # жоден не годиться — стоп
            break
        seq.append(c)
        seen.add(tail + (c,))
    return seq[:k ** n]                     # циклічна частина
