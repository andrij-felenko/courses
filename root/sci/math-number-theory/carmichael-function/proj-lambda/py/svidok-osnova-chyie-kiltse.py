def multiplicative_order(a, n):
    """ord(a): найменший m>0 з a^m ≡ 1 (mod n). Взаємна простота обов'язкова."""
    if gcd(a, n) != 1:
        raise ValueError("порядок визначено лише за gcd(a, n) = 1")
    order = carmichael_lambda(n)            # ord(a) неодмінно ділить λ(n)
    for p, _ in factorize(order):
        while order % p == 0 and pow(a, order // p, n) == 1:
            order //= p                     # цей простий множник у показнику зайвий
    return order

assert multiplicative_order(3, 8)  == 2
assert multiplicative_order(2, 11) == 10   # 2 — первісний корінь за модулем 11
