from math import gcd

# ── Елемент кільця лишків ℤ/n: значення завжди зведене в діапазон 0…n−1 ──
class Zn:
    def __init__(self, value, mod):
        self.n = mod
        self.v = value % mod          # у Python % за додатного модуля вже невід'ємний — «+ n» не треба
    def __add__(self, o):  return Zn(self.v + o.v, self.n)
    def __mul__(self, o):  return Zn(self.v * o.v, self.n)   # цілі Python необмежені — переповнення нема
    def __eq__(self, o):   return (self.v, self.n) == (o.v, o.n)
    def __repr__(self):    return f"{self.v} (mod {self.n})"

# ── Розширений Евклід: gcd(a, b) + коефіцієнти Безу  (a·x + b·y = gcd) ──
def egcd(a, b):
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

# ── Обернений за множенням до a у ℤ/n, або None, якщо його нема ──
def inverse(a, n):
    g, x, _ = egcd(a % n, n)
    if g != 1:                        # gcd ≠ 1 → взаємно не прості → оберненого нема
        return None
    return x % n                      # коефіцієнт Безу x — і є обернений

N = 12
print(f"3 * 4 = {Zn(3, N) * Zn(4, N)}\n")

print("  *  |" + "".join(f"{b:3}" for b in range(N)))                       # шапка
print("-----+" + "---" * N)
for a in range(N):                                                         # тіло: a·b
    print(f"{a:3}  |" + "".join(f"{(Zn(a, N) * Zn(b, N)).v:3}" for b in range(N)))

units = [a for a in range(1, N) if inverse(a, N) is not None]              # скан
zdiv  = [a for a in range(1, N) if inverse(a, N) is None]
print("\nодиниці (оборотні): " + "".join(f"{a:3}" for a in units))
print("дільники нуля:      " + "".join(f"{a:3}" for a in zdiv))
