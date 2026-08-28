def turbo_decode(Ls, Lp1, Lp2, perm, inv, niters):
    N = len(Ls)
    Lsp = [Ls[perm[i]] for i in range(N)]     # систематичні у переставленому порядку
    La1 = [0.0]*N                             # спершу апріорі немає
    hist = []
    for _ in range(niters):
        Le1 = siso(Ls,  Lp1, La1)             # декодер 1 — прямий контроль
        La2 = [Le1[perm[i]] for i in range(N)]      # → переставити для декодера 2
        Le2 = siso(Lsp, Lp2, La2)             # декодер 2 — переставлений контроль
        La1 = [Le2[inv[i]] for i in range(N)]       # ← розставити назад
        bits = [1 if Ls[k] + La1[k] + Le1[k] > 0 else 0 for k in range(N)]
        hist.append(bits)                     # рішення після цього оберту
    return hist
