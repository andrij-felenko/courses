from math import log

def H(P, base=2):
    """Ентропія розподілу P: base=2 → біти, base=e → нати."""
    return -sum(p * log(p, base) for p in P if p > 0)

# 1. Групування: той самий вибір, порахований двома способами
straight = H([1/2, 1/3, 1/6])                      # прямо, три наслідки
in_steps = H([1/2, 1/2]) + 1/2 * H([2/3, 1/3])     # монета, тоді ще вибір
print(straight, in_steps)     # 1.4591479170272448 1.4591479170272448 — збіг точний

# 2. Те саме на потоці станів: рахуємо групами, а не одним махом
stream = {"ok": 0.80, "warn": 0.12, "err_a": 0.05, "err_b": 0.03}
groups = {"norm": ["ok", "warn"], "err": ["err_a", "err_b"]}

flat  = H(list(stream.values()))                                   # 0.992473 біта
w     = {g: sum(stream[s] for s in ss) for g, ss in groups.items()}   # ваги груп
outer = H(list(w.values()))                                        # між групами: 0.402179
inner = sum(w[g] * H([stream[s] / w[g] for s in ss])               # всередині, зважено
            for g, ss in groups.items())                           # 0.590294
print(flat, outer + inner)    # 0.9924729340122933 0.9924729340122933 — знову точно

# 3. Пастка: більшість бібліотек рахує в НАТАХ, не в бітах
from scipy.stats import entropy
print(entropy([0.5, 0.25, 0.25]))          # 1.0397... — це нати!
print(entropy([0.5, 0.25, 0.25], base=2))  # 1.5 — а це біти
