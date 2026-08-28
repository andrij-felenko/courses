import math

def f(x):
    return 4.0 * x * (1.0 - x)

a, b = 0.400000000, 0.400000001      # різниця 1e-9

for n in range(46):
    d = abs(a - b)
    print("n=%2d  A=%.9f  B=%.9f  |A-B|=%.3e  log2=%6.2f"
          % (n, a, b, d, math.log2(d)))
    a, b = f(a), f(b)
