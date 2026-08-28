# ── Вирок: порівняти з порогом, надрукувати бік і запас ───────────────
def verdict(what: str, value: int, threshold: int) -> None:
    if value == 0:
        print(f"{what}: оцінка 0 — щось не так у припущеннях")
        return
    if value <= threshold:
        # запас = у скільки разів поріг більший за оцінку (ціла частина)
        margin = threshold // value
        print(f"{what}: {value} <= поріг {threshold}  ->  ВЛАЗИТЬ (запас x{margin})")
    else:
        over = value // threshold
        print(f"{what}: {value} >  поріг {threshold}  ->  НЕ ВЛАЗИТЬ (перевищення x{over})")
