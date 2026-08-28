import random

# вибір дії: з імовірністю eps — випадкова (розвідка),
# інакше — з найбільшим Q (визиск)
def choose_action(q_row, eps):
    # random.random() — псевдовипадкове число в [0,1)
    if random.random() < eps:
        return random.randrange(len(q_row))   # розвідка: будь-яка дія

    # визиск: argmax по Q
    best = 0
    for j in range(1, len(q_row)):
        if q_row[j] > q_row[best]:
            best = j
    return best
