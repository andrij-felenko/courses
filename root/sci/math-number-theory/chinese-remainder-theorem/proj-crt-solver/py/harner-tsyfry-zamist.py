def garner_digits(residues, moduli):
    """Мішано-основні цифри: x = d[0] + d[1]·n[0] + d[2]·n[0]n[1] + …"""
    k = len(moduli)
    inv = [[0] * k for _ in range(k)]                # inv[i][j] = n[j]⁻¹ mod n[i]
    for i in range(k):                               # модулі сталі → таблиця рахується РАЗ
        for j in range(i):
            inv[i][j] = pow(moduli[j], -1, moduli[i])
    d = [0] * k
    for i in range(k):
        di = residues[i] % moduli[i]
        for j in range(i):
            di = (di - d[j]) * inv[i][j] % moduli[i]  # обидва множники < n[i]: стеля n[i]²
        d[i] = di
    return d

def garner(residues, moduli):
    d = garner_digits(residues, moduli)
    x, weight = 0, 1
    for di, ni in zip(d, moduli):                    # ЛИШЕ тут число доростає до N
        x += di * weight
        weight *= ni
    return x

print(garner_digits([2, 3, 2], [3, 5, 7]))   # [2, 2, 1]
print(garner([2, 3, 2], [3, 5, 7]))          # 23 = 2 + 2·3 + 1·15
