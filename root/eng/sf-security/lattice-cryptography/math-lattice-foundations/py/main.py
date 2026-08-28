def grams_schmidt(B):
    n = len(B)
    B_star = [[0.0]*len(B[0]) for _ in range(n)]
    mu = [[0.0]*n for _ in range(n)]
    for i in range(n):
        B_star[i] = list(B[i])
        for j in range(i):
            dot_bb = sum(B[i][k] * B_star[j][k] for k in range(len(B[0])))
            dot_star = sum(B_star[j][k] ** 2 for k in range(len(B[0])))
            mu[i][j] = dot_bb / dot_star if dot_star != 0 else 0.0
            for k in range(len(B[0])):
                B_star[i][k] -= mu[i][j] * B_star[j][k]
    return B_star, mu

def lll_reduce(B, delta=0.75):
    n = len(B)
    B = [list(row) for row in B]
    k = 1
    while k < n:
        B_star, mu = grams_schmidt(B)
        # 1. Розмірна редукція для k по відношенню до j
        for j in range(k - 1, -1, -1):
            if abs(mu[k][j]) > 0.5:
                q = round(mu[k][j])
                for m in range(len(B[0])):
                    B[k][m] -= q * B[j][m]
                B_star, mu = grams_schmidt(B)

        # 2. Перевірка умови Ловаса
        dot_k = sum(B_star[k][m]**2 for m in range(len(B[0])))
        dot_k1 = sum(B_star[k-1][m]**2 for m in range(len(B[0])))
        if dot_k >= (delta - mu[k][k-1]**2) * dot_k1:
            k += 1
        else:
            # Обмін векторів місцями
            B[k], B[k-1] = B[k-1], B[k]
            k = max(k - 1, 1)
    return B

# Приклад застосування
B_bad = [[1, 15], [0, 1]]
B_good = lll_reduce(B_bad)
