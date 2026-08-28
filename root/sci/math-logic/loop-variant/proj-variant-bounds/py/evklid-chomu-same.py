def gcd_steps(a, b):
    k = 0
    while b:
        a, b = b, a % b
        k += 1
    return k

# найменша пара a > b > 0, що вимагає k кроків
def min_pair(k, cap=400):
    for b in range(1, cap):
        for a in range(b + 1, 2 * cap):
            if gcd_steps(a, b) >= k:
                return a, b
