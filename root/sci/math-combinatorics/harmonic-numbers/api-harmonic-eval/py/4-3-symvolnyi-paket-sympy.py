import sympy as sp

n = sp.Symbol('n')
# Символьне представлення H[n]
expr = sp.harmonic(n)

# Асимптотичний розклад у ряд Тейлора при n -> oo
series_expr = sp.series(sp.harmonic(n), n, sp.oo, n=4)
print("Асимптотичний ряд sympy:")
print(series_expr)

# Обчислення з 50 знаками точності
val_50 = sp.harmonic(100).evalf(50)
print("H[100] з 50 знаками:", val_50)
