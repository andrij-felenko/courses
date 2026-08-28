from math import gcd

def gcd_all(xs: list[int]) -> int:
    g = 0                                # нейтральний елемент: НСД(0, x) = x
    for x in xs:
        g = gcd(g, x)
        if g == 1:
            return 1                     # одиницю вже ніщо не зрушить
    return g

# Від Python 3.9 math.gcd бере скільки завгодно аргументів: gcd(*xs).
# Зручно, але дострокового виходу ви вже не контролюєте.
