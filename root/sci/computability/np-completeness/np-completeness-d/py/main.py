def verify(numbers, target, certificate):
    # certificate — обрана підмножина (список чисел зі списку numbers)
    # перевірка: (1) усе взяте справді є серед чисел; (2) сума збігається з ціллю
    pool = list(numbers)
    for x in certificate:
        if x not in pool:
            return False          # свідок посилається на число, якого нема
        pool.remove(x)            # кожне число можна взяти лише раз
    return sum(certificate) == target

# {3, 34, 4, 12, 5, 2}, ціль 9  →  свідок [4, 5]  дає 4 + 5 = 9  → True
