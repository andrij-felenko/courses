U = list(range(8))                  # всесвіт: 8 елементів
full = set(U)                       # сам всесвіт як множина

def subset(mask):                   # маска (число) → підмножина U
    return {U[i] for i in range(len(U)) if mask >> i & 1}

def de_morgan_holds():
    N = 1 << len(U)                 # 2⁸ = 256 підмножин
    for a in range(N):
        A = subset(a)
        for b in range(N):
            B = subset(b)
            left  = full - (A | B)          # (A ∪ B)ᶜ
            right = (full - A) & (full - B)  # Aᶜ ∩ Bᶜ
            if left != right:
                return False, (A, B)         # знайшли контрприклад
    return True, None                        # усі 256·256 пар збіглися

print(de_morgan_holds())            # (True, None)
