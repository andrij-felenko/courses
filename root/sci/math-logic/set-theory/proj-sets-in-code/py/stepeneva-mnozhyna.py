def powerset(xs):
    xs = list(xs)
    n = len(xs)
    for mask in range(1 << n):        # 0, 1, …, 2ⁿ−1  (1 << n  це 2ⁿ)
        # лишаємо ті елементи, чий біт у масці стоїть
        yield [xs[i] for i in range(n) if mask >> i & 1]

for sub in powerset(['a', 'b', 'c']):
    print(sub)
# []               ← маска 000
# ['a']            ← маска 001   (стоїть біт 0)
# ['b']            ← маска 010   (біт 1)
# ['a', 'b']       ← маска 011
# ['c']            ← маска 100   (біт 2)
# ['a', 'c']       ← маска 101
# ['b', 'c']       ← маска 110
# ['a', 'b', 'c']  ← маска 111
