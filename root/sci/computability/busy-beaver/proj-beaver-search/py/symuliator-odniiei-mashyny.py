def simulate(table, n, cap):
    tape = {}                              # позиція → символ (0 за замовчуванням)
    h = st = steps = 0
    while True:
        a = table[st * 2 + tape.get(h, 0)]
        tape[h] = a & 1                    # write
        steps += 1
        t = a >> 2                         # target
        if t == n:                         # перейшли в стан зупинки
            return True, steps, sum(tape.values())
        h += 1 if (a >> 1) & 1 else -1     # dir: 1 = праворуч
        st = t
        if steps >= cap:                   # СТЕЛЯ — далі не женемо
            return False, steps, sum(tape.values())
