# Простий відтворюваний ГПВЧ (xorshift32): один seed → один і той самий
# поділ. Відтворюваність тут не примха: та сама розбивка потрібна, щоб
# чесно порівнювати дві моделі на однакових блоках, і щоб баг можна було
# відтворити. random зі stdlib для цього гірший — залежить від платформи.
_MASK = 0xFFFFFFFF       # тримаємо стан у межах 32 біт
_rng_state = 0

def rng_seed(s: int) -> None:
    global _rng_state
    _rng_state = s if s else 0x1234567   # нуль зациклив би xorshift на нулі

def rng_next() -> int:
    global _rng_state
    x = _rng_state
    x ^= (x << 13) & _MASK
    x ^= x >> 17
    x ^= (x << 5) & _MASK
    _rng_state = x & _MASK
    return _rng_state

# Рівномірне ціле в [0, m) без модуло-зсуву:
# наївне rng_next() % m трохи частішає малі залишки, коли 2³² не кратне m.
# Відкидаємо «хвіст», що псує рівномірність.
def rng_below(m: int) -> int:
    limit = _MASK - (_MASK % m)      # найбільше кратне m
    while True:
        r = rng_next()
        if r < limit:
            return r % m

# Перемішати order[0..n-1] на місці (Фішер–Єйтс, прохід із кінця).
def shuffle(order: list[int], n: int) -> None:
    for i in range(n - 1, 0, -1):
        j = rng_below(i + 1)                     # j ∈ [0, i] включно
        order[i], order[j] = order[j], order[i]
