def karatsuba(x, y):
    # БАЗОВИЙ ВИПАДОК: дрібні числа множимо прямо
    if x < 10 or y < 10:
        return x * y
    # РОЗДІЛИТИ: ріжемо кожне число навпіл за розрядами
    m = min(len(str(x)), len(str(y))) // 2
    base = 10 ** m
    xa, xb = divmod(x, base)                 # старша й молодша половини x
    ya, yb = divmod(y, base)                 # старша й молодша половини y
    # ПІДКОРИТИ: три множення замість чотирьох (тим самим методом, рекурсивно)
    hi    = karatsuba(xa, ya)                # старша·старша
    lo    = karatsuba(xb, yb)                # молодша·молодша
    mid   = karatsuba(xa + xb, ya + yb)      # (сума)·(сума) — одне зайве множення
    cross = mid - hi - lo                    # = xa·yb + xb·ya, БЕЗ окремого множення
    # ПОЄДНАТИ: зсуви за розрядами й додавання
    return hi * base * base + cross * base + lo
