import secrets

def is_probable_prime(n: int, rounds: int = 40) -> bool:
    if n < 2:
        return False
    for small in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % small == 0:
            return n == small          # дешеве сито: відсіює ~80% кандидатів
    d, s = n - 1, 0
    while d % 2 == 0:                  # n − 1 = d · 2ˢ, d непарне
        d //= 2
        s += 1
    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2       # свідок a ∈ 2 … n−2
        x = powmod(a, d, n)
        if x == 1 or x == n - 1:
            continue                   # цей свідок нічого не виказав
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break                  # дійшли до −1 → свідок мовчить
        else:
            return False               # жодного −1 → свідок спіймав: складене
    return True

def gen_prime(bits: int) -> int:
    """Випадкове просте потрібної довжини — тягнемо, доки не пощастить."""
    while True:
        cand = secrets.randbits(bits) | (3 << (bits - 2)) | 1
        #                                ↑ два старші біти ↑ непарність:
        #                                тримають довжину   парні відсіює одразу
        if is_probable_prime(cand):
            return cand
