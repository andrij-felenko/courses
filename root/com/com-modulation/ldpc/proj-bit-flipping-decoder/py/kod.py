"""Жорсткий декодер LDPC: перевертання бітів (Галлагер, 1963).

checks[j] — список індексів бітів, які накриває перевірка j.
Слово — список 0/1 завдовжки n.
"""

def parity(word, bits):
    """Парність групи бітів: XOR усіх, кого накриває перевірка."""
    acc = 0
    for i in bits:
        acc ^= word[i]
    return acc


def bit_checks_of(checks, n):
    """Обернений список суміжності: біт -> перевірки, у яких він сидить."""
    owners = [[] for _ in range(n)]
    for j, bits in enumerate(checks):
        for i in bits:
            owners[i].append(j)
    return owners


def syndrome(checks, word):
    """s[j] = 0, якщо перевірка j сходиться. Ціна — O(ребер), не O(m·n)."""
    return [parity(word, bits) for bits in checks]


def decode(checks, n, received, max_iter=50):
    """Повертає (слово, скільки ітерацій, чи зійшлося).

    Увага: True означає лише H·ĉᵀ = 0 — що слово кодове,
    а не що воно те саме, яке надіслали.
    """
    word = list(received)
    owners = bit_checks_of(checks, n)
    s = syndrome(checks, word)              # рахуємо ОДИН раз

    for it in range(max_iter):
        if not any(s):
            return word, it, True

        # скільки порушених перевірок звинувачує кожен біт
        worst, worst_score = -1, 0
        for i in range(n):
            score = sum(s[j] for j in owners[i])
            if score > worst_score:         # строге > : за нічиєї виграє менший індекс
                worst, worst_score = i, score

        if worst < 0:
            return word, it, False          # звинуватити нікого — глухий кут

        word[worst] ^= 1
        for j in owners[worst]:             # інкрементно: лише перевірки цього біта
            s[j] ^= 1

    return word, max_iter, not any(s)       # вичерпали ліміт


if __name__ == "__main__":
    # (2,3)-регулярний код на 6 бітів: кожен біт у 2 перевірках, кожна на 3 бітах
    CHECKS = [[0, 1, 2], [0, 3, 4], [1, 3, 5], [2, 4, 5]]
    N = 6

    print(decode(CHECKS, N, [1, 1, 1, 0, 1, 1]))   # канал побив b2
    print(decode(CHECKS, N, [0, 1, 0, 0, 1, 0]))   # канал побив b0 і b5
