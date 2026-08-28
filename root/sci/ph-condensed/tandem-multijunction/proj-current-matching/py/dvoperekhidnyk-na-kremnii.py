def top_by_power(bottom=1.11):
    "Верхній поріг під максимум потужності на заданому низі, еВ."
    grid = np.arange(1.40, 2.00, 0.01)
    return round(float(max(grid, key=lambda t: power([t, bottom]))), 2)

>>> for W in (0.25, 0.40, 0.55):
...     Woc = W; print(W, "->", top_by_power())
0.25 -> 1.7
0.4 -> 1.7
0.55 -> 1.7
>>> Woc = 0.40      # повертаємо робоче значення
