def de_bruijn_hierholzer(k, n):
    m = k ** (n - 1)                 # вершини: слова довжини n-1, як числа 0..m-1
    nxt = [0] * m                    # наступний невитрачений вихідний символ вершини
    stack = [(0, -1)]                # (вершина, символ ребра, яким сюди зайшли)
    seq = []
    while stack:
        v, sym = stack[-1]
        if nxt[v] < k:               # є ще невитрачене ребро — заходимо глибше
            c = nxt[v]
            nxt[v] += 1
            stack.append(((v * k + c) % m, c))
        else:                        # глухий кут — відступаємо, записуючи ребро
            stack.pop()
            if sym != -1:
                seq.append(sym)
    seq.reverse()
    return seq
