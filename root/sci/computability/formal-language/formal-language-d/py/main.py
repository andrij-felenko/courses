from itertools import count, product

def sigma_star(alphabet):
    """Усі слова над alphabet у шортлекс-порядку: коротші раніше,
    рівні за довжиною — за абеткою. Перелік нескінченний."""
    for n in count(0):                       # довжина 0, 1, 2, …
        for letters in product(alphabet, repeat=n):
            yield "".join(letters)           # n = 0 дає рівно одне слово: ε

words = sigma_star("ab")
print([next(words) for _ in range(8)])
# ['', 'a', 'b', 'aa', 'ab', 'ba', 'bb', 'aaa']
