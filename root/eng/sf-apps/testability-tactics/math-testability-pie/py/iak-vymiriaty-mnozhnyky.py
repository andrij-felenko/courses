import random
def bucket(s):                       # стискання: число → 3 кошики (велика DRR)
    return 0 if s < 300 else (1 if s < 700 else 2)
def state_orig(x): return x          # «стан після рядка» в оригіналі
def state_mut(x):  return x + 5      # мутант псує стан на +5

N = 200_000
weak = strong = 0
for _ in range(N):
    x = random.randint(0, 1000)
    so, sm = state_orig(x), state_mut(x)
    if so != sm:                    weak   += 1     # слабке: стан різний?  (R·I)
    if bucket(so) != bucket(sm):    strong += 1     # сильне: вихід різний? (R·I·P)

print(round(weak/N, 3), round(strong/N, 4))         # ≈ 1.0    ≈ 0.010
print("p_пош ≈", round((strong/N) / (weak/N), 4))   # ≈ 0.010
