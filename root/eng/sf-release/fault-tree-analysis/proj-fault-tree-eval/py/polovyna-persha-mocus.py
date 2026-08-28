# Дерево: словник вентилів. Базова подія — ім'я, якого НЕМА серед ключів.
tree = {
    "TOP":   ("or",  ["POWER", "PUMPS"]),
    "PUMPS": ("and", ["PUMP_A", "PUMP_B"]),
}

def mocus(tree, top):
    """Матриця перерізів. АБО множить рядки, І дописує стовпці."""
    work = [frozenset([top])]          # рядки, де ще лишилися вентилі
    cuts = set()                       # рядки з самих базових подій
    while work:
        row = work.pop()
        gate = next((s for s in row if s in tree), None)
        if gate is None:               # у рядку самі базові події → переріз-кандидат
            cuts.add(row)
            continue
        rest = row - {gate}
        kind, inputs = tree[gate]
        if kind == "and":              # І: усі входи в ТОЙ САМИЙ рядок (ширший набір)
            work.append(rest | set(inputs))
        else:                          # АБО: окремий рядок на КОЖЕН вхід (більше наборів)
            for g in inputs:
                work.append(rest | {g})
    return cuts

def minimal(cuts):
    """Поглинання: лишити тільки набори, всередині яких нема меншого перерізу."""
    out = []
    for c in sorted(cuts, key=len):        # від найменших до найбільших
        if not any(m <= c for m in out):   # c не містить уже знайденого перерізу?
            out.append(c)
    return out

for c in minimal(mocus(tree, "TOP")):
    print(sorted(c))
# ['POWER']
# ['PUMP_A', 'PUMP_B']
