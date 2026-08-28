RUNNING, DONE = 0, 1

def halts_within(step, state, budget):
    """Напівсуддя: женемо не більш як budget кроків.
    Повертає ('HALTS', кроки) або ('UNKNOWN', кроки) — ніколи 'LOOPS'."""
    for i in range(budget):
        status, state = step(state)
        if status == DONE:
            return ("HALTS", i + 1)     # достеменно спинилась — ми бачили
    return ("UNKNOWN", budget)          # бюджет вичерпано — не знаємо

def countdown(s):                       # рахує вниз до 0, тоді спиняється
    return (DONE, s) if s <= 0 else (RUNNING, s - 1)

def forever(s):                         # вічна
    return (RUNNING, s)

def heavy(s):                           # уся праця — в одному кроці
    acc = sum(range(2_000_000))         # мільйони додавань під одним кроком
    return (DONE, acc)

print("countdown(50),  б=10000 -> %-7s кроків %d" % halts_within(countdown, 50,  10000))
print("forever,        б=10000 -> %-7s кроків %d" % halts_within(forever,   0,   10000))
print("countdown(500), б=100   -> %-7s кроків %d" % halts_within(countdown, 500, 100))
print("countdown(500), б=5000  -> %-7s кроків %d" % halts_within(countdown, 500, 5000))
print("heavy,          б=5     -> %-7s кроків %d" % halts_within(heavy,     0,   5))
