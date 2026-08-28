G = (0b111, 0b101)        # генератори g1 = 7₈, g2 = 5₈
K = 3
NSTATE = 1 << (K - 1)     # 2^(K−1) = 4 стани

def parity(x):            # XOR усіх бітів числа: 0 або 1
    return bin(x).count("1") & 1

# Ґратку рахуємо раз: для кожного (стан, вхід) — пара виходів і наступний стан.
TRELLIS = {}
for s in range(NSTATE):
    for u in (0, 1):
        w = (u << (K - 1)) | s            # трибітове вікно [uₖ u₍ₖ₋₁₎ u₍ₖ₋₂₎]
        out = (parity(w & G[0]), parity(w & G[1]))
        TRELLIS[(s, u)] = (out, w >> 1)   # (виходи, наступний стан)
