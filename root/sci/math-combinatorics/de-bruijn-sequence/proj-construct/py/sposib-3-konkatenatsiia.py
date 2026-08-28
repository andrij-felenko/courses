def de_bruijn_fkm(k, n):
    a = [0] * (n + 1)               # a[1..n] — поточне слово-кандидат
    seq = []
    def gen(t, p):                  # t: заповнено символів; p: довжина періоду
        if t > n:
            if n % p == 0:          # період p ділить n → слово Ліндона довжини p
                seq.extend(a[1:p + 1])
        else:
            a[t] = a[t - p]         # менша гілка: продовжити період
            gen(t + 1, p)
            for c in range(a[t - p] + 1, k):   # більший символ рве період
                a[t] = c
                gen(t + 1, t)
    gen(1, 1)
    return seq
