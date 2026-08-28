def f_node(a, b):                      # обережно: min-sum boxplus
    return (1 if a >= 0 else -1) * (1 if b >= 0 else -1) * min(abs(a), abs(b))

def g_node(a, b, u):                   # u — уже вирішений верхній біт
    return b + (1 - 2 * u) * a

def sc_decode(llr, frozen):
    """llr — N довір на виходах цього вузла; frozen — маска (True = заморожено).
    Повертає (û, x): вирішені біти й відповідне кодове слово (частинкові суми)."""
    n = len(llr)
    if n == 1:
        bit = 0 if frozen[0] else (0 if llr[0] >= 0 else 1)
        return [bit], [bit]
    h = n // 2
    La = [f_node(llr[i], llr[i + h]) for i in range(h)]      # f-прохід
    u_up, x_up = sc_decode(La, frozen[:h])                   # верхня половина
    Lb = [g_node(llr[i], llr[i + h], x_up[i]) for i in range(h)]   # g-прохід
    u_lo, x_lo = sc_decode(Lb, frozen[h:])                   # нижня половина
    u = u_up + u_lo
    x = [x_up[i] ^ x_lo[i] for i in range(h)] + x_lo         # ті самі XOR, що й кодер
    return u, x

# --- запуск: N=8, заморожені позиції {0,1,2,4}, решта — дані ---
frozen = [True, True, True, False, True, False, False, False]
llr    = [-4, 2, 3, 1, 5, -2, 3, -6]        # м'які виходи каналу (LLR)
u_hat, x_hat = sc_decode(llr, frozen)
print(u_hat)      # -> [0, 0, 0, 1, 0, 0, 1, 1]
