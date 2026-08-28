from dataclasses import dataclass

@dataclass
class Layer:
    name: str
    tries: int                     # скільки спроб робить шар (1 = без повтору)

# СТЕЛЯ: добуток спроб усіх шарів — кожна спроба провалюється, кожен шар вичерпує повтори.
def worst_case(layers):
    acc = 1
    for l in layers:
        acc *= l.tries
    return acc

# ОЧІКУВАНИЙ фан-аут за ймовірності збою p: шар на t спроб шле в середньому
# 1 + p + p² + … + p^(t−1) запитів (повторює лише ПІСЛЯ збою).
def expected_per_layer(tries, p):
    s, term = 0.0, 1.0
    for _ in range(tries):
        s += term
        term *= p
    return s                       # = (1 − p**tries) / (1 − p) при p < 1

def expected_fanout(layers, p):
    acc = 1.0
    for l in layers:
        acc *= expected_per_layer(l.tries, p)
    return acc

path = [Layer("застосунок", 3), Layer("шлюз", 3), Layer("сайдкар", 3)]
RPS = 500                          # клік/с на ранковому піку

for p in (0.0, 0.3, 0.7, 1.0):
    f = expected_fanout(path, p)
    print(f"p={p}: фан-аут {f:.2f}× → {round(f * RPS)} req/s")
print(f"стеля: {worst_case(path)}× → {worst_case(path) * RPS} req/s")
