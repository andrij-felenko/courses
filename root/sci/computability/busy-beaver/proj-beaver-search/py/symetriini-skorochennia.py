import sys
sys.setrecursionlimit(100_000)

def hunt_tnf(n, cap):
    st = {"leaves": 0, "halted": 0, "holdouts": 0, "best_ones": 0, "best_steps": 0}

    def simulate(table):                        # симуляція з ЧАСТКОВОЮ таблицею
        tape = {}; h = s = steps = 0
        while True:
            key = (s, tape.get(h, 0))
            if key not in table:                # клітинку ще не визначено —
                return ("undef", key)           # час розгалужуватись
            w, d, t = table[key]
            tape[h] = w; steps += 1
            if t == n:
                return ("halt", steps, sum(tape.values()))
            h += 1 if d == 1 else -1; s = t
            if steps >= cap:
                return ("cap", steps, sum(tape.values()))

    def search(table, used):                    # used — скільки станів уже введено
        r = simulate(table)
        if r[0] == "halt":
            _, steps, ones = r
            st["leaves"] += 1; st["halted"] += 1
            st["best_ones"]  = max(st["best_ones"],  ones)
            st["best_steps"] = max(st["best_steps"], steps)
            return
        if r[0] == "cap":
            st["leaves"] += 1; st["holdouts"] += 1   # недобиток: не класифікувати
            return
        _, cell = r                              # невизначена клітинка → гілкуємось
        targets = list(range(used)) + ([used] if used < n else [])  # вжиті + ОДИН новий
        for w in (0, 1):
            for d in (0, 1):                     # 0=L, 1=R
                for t in targets:
                    nxt = dict(table); nxt[cell] = (w, d, t)
                    search(nxt, max(used, t + 1))
        for w in (0, 1):                         # зупинка: напрям байдужий — одна гілка
            nxt = dict(table); nxt[cell] = (w, 1, n)
            search(nxt, used)

    search({(0, 0): (1, 1, 1)}, 2)               # старт A,0=(1,R,B); стани A,B уведено
    return st
