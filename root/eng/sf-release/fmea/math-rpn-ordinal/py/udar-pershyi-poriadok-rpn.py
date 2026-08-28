# контрприклад — не одиничний: переберімо ВСІ зростні перенумерації
# мітками із запасу 1…20 і порахуймо, як часто добуток перекидає пару
from itertools import combinations

A, B = (9, 2, 8), (4, 6, 10)          # подвійне списання vs застаріла ціна
prod = lambda t, f: f[t[0]] * f[t[1]] * f[t[2]]

ident = {k: k for k in range(1, 11)}
base = prod(A, ident) > prod(B, ident)
flip = total = 0
for pick in combinations(range(1, 21), 10):        # будь-які 10 зростних міток
    f = {k: pick[k - 1] for k in range(1, 11)}     # 1→pick[0] < 2→pick[1] < …
    total += 1
    if (prod(A, f) > prod(B, f)) != base:
        flip += 1

print(f"зростних перенумерацій: {total}")
print(f"перекидають порядок пари: {flip}  ({100 * flip / total:.1f}%)")
# зростних перенумерацій: 184756
# перекидають порядок пари: 6938  (3.8%)
