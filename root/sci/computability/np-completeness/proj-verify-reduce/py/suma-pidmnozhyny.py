from collections import Counter

def verify_subset_sum(numbers, target, cert):
    """Свідок cert — обрана підмножина. True, якщо (1) усе взяте справді
    є серед numbers у потрібній кількості і (2) сума дорівнює цілі."""
    pool = Counter(numbers)          # скільки разів кожне число доступне
    for x in cert:
        if pool[x] <= 0:
            return False             # свідок бере число, якого вже (чи взагалі) нема
        pool[x] -= 1                 # витратили одну «копію»
    return sum(cert) == target
