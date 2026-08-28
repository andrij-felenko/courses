from dataclasses import dataclass

@dataclass
class Option:
    name: str
    avail_pct: float      # СИРА доступність, % — для перевірки обмеження
    scores: dict          # бали 0..5 за атрибутами — для суми вподобань

W = {"вартість": 5, "доступність": 4, "швидкодія": 3, "безпека": 4}

A = Option("A: один регіон",  99.00, {"вартість": 5, "доступність": 1, "швидкодія": 5, "безпека": 4})
B = Option("B: мультирегіон", 99.95, {"вартість": 2, "доступність": 5, "швидкодія": 4, "безпека": 4})
options = [A, B]

def weighted_sum(o):
    return sum(W[k] * o.scores[k] for k in W)

# ── Наївно: доступність — просто одна з ваг, поріг «розчинено» в сумі ──
print("наївна зважена сума (обмеження як м'яка вага):")
for o in sorted(options, key=weighted_sum, reverse=True):
    print(f"  {o.name:16} сума = {weighted_sum(o)}")

# ── Чесно: спершу фільтр твердого порога, тоді сума серед дійсних ──
FLOOR = 99.9   # доступність ≥ 99.9% — закон, не вподобання
feasible = [o for o in options if o.avail_pct >= FLOOR]
best = max(feasible, key=weighted_sum) if feasible else None
print("\nчесно (фільтр порога, тоді сума серед дійсних):")
for o in options:
    if o.avail_pct >= FLOOR:
        print(f"  {o.name:16} дійсний, сума = {weighted_sum(o)}")
    else:
        print(f"  {o.name:16} ВІДСІЯНО ({o.avail_pct:.2f}% < {FLOOR}%)")
print(f"  → вибір: {best.name if best else 'нема дійсних'}")
