from itertools import combinations

n = 3
maj   = lambda k: bin(k).count("1") >= 2          # більшість одиниць у 3 бітах
truth = [int(maj(k)) for k in range(1 << n)]      # таблиця значень МАЖ

def mobius(v):                                    # каскад SOS — той самий в обидва боки
    v = v[:]
    for i in range(n):
        for k in range(1 << n):
            if k >> i & 1:
                v[k] ^= v[k ^ (1 << i)]
    return v

coef = mobius(truth)
assert mobius(coef) == truth                      # інволюція: двічі — тотожність

bit = lambda A: sum(1 << i for i in A)            # підмножина індексів → номер входу
def c(S):                                         # формула c_S = ⊕(f(T) : T ⊆ S)
    r = 0
    for m in range(len(S) + 1):
        for T in combinations(S, m):
            r ^= truth[bit(T)]
    return r

assert c((0, 1))    == coef[bit((0, 1))]    == 1                       # при a·b — одиниця
assert c((0, 1, 2)) == coef[bit((0, 1, 2))] == truth.count(1) % 2 == 0  # верхній = парність ваги
print("формула c_S і каскад збігаються; M(M(f)) == f")
