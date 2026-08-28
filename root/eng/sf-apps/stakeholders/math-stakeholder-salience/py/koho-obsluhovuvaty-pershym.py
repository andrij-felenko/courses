from itertools import permutations

# (назва, вартість зволікання за одиницю часу, тривалість)
jobs = [
    ("журнал аудиту",       13, 2),
    ("пришвидшення оплати",  8, 3),
    ("мультирегіон",        13, 8),
]

def total_delay_cost(order):
    t, cost = 0, 0
    for _, w, p in order:
        t += p             # момент завершення цієї роботи
        cost += w * t      # накопичена вартість зволікання: w · C
    return cost

# Справжній оптимум — грубий перебір усіх 3! порядків.
best = min(permutations(jobs), key=total_delay_cost)
# Правило WSJF — спадання відношення (вартість зволікання / тривалість).
wsjf = sorted(jobs, key=lambda j: j[1] / j[2], reverse=True)

print("перебором:", " → ".join(n for n, _, _ in best), "| ціна =", total_delay_cost(best))
print("за WSJF:  ", " → ".join(n for n, _, _ in wsjf), "| ціна =", total_delay_cost(wsjf))
for n, w, p in wsjf:
    print(f"  {n:22} WSJF = {w}/{p} = {w / p:.2f}")
