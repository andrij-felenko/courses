# GF(2^4) з примітивним x^4 + x + 1 (0b10011): 15 ненульових елементів.
M = 4
N = 15
exp_of = [0] * N        # exp_of[i] = alpha^i як 4-бітовий вектор
log_of = [0] * (N + 1)  # log_of[v] = i, де alpha^i = v

def gf_init():
    v = 1
    for i in range(N):
        exp_of[i] = v
        log_of[v] = i
        v <<= 1
        if v & (1 << M):
            v ^= 0b10011            # згорнути назад у поле

def gf_mul(a, b):
    if not a or not b:
        return 0
    return exp_of[(log_of[a] + log_of[b]) % N]   # множення = додавання показників

def gf_inv(a):                                   # ділення через від'ємний показник
    return exp_of[(N - log_of[a]) % N]

def main():
    gf_init()

    # Помилки на позиціях 3 і 10  ->  e(x) = x^3 + x^10.
    # Синдром Sj = r(alpha^j) = alpha^(3j) + alpha^(10j)  (дані занулюються).
    S = [0] * 5
    for j in range(1, 5):
        S[j] = exp_of[(3 * j) % N] ^ exp_of[(10 * j) % N]
    print(f"S1..S4 = {S[1]} {S[2]} {S[3]} {S[4]}")

    # Локатор для двох помилок: sigma(x) = 1 + s1*x + s2*x^2.
    s1 = S[1]
    s1cube = gf_mul(gf_mul(S[1], S[1]), S[1])     # S1^3
    s2 = gf_mul(S[3] ^ s1cube, gf_inv(S[1]))      # (S3 + S1^3)/S1

    # Пошук Ченя: корінь sigma у x = alpha^(-i)  ->  помилка на позиції i.
    positions = []
    for i in range(N):
        xi = exp_of[(N - i) % N]                  # alpha^(-i)
        val = 1 ^ gf_mul(s1, xi) ^ gf_mul(s2, gf_mul(xi, xi))
        if val == 0:
            positions.append(i)
    print("позиції помилок:", *positions)         # друкує: S1..S4 = 15 10 11 8 / позиції: 3 10

if __name__ == "__main__":
    main()
