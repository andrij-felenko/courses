class LockController:
    def __init__(self):
        self._handled = set()   # id уже виконаних наказів
        self._actuations = 0    # скільки разів реально клацнув замок

    def handle(self, cmd):
        if cmd["id"] in self._handled:   # повтор тієї самої особи — дубль
            return
        self._handled.add(cmd["id"])
        self._actuations += 1            # фізичний рух засува

    @property
    def physical_opens(self):
        return self._actuations


# ── Фітнес-функція: падає в збірці, щойно міру порушено ──
def fitness_lock_opens_exactly_once():
    # 1) хитка мережа: клієнт повторив ОДИН наказ п'ять разів
    one = LockController()
    for _ in range(5):
        one.handle({"id": "cmd-42", "action": "open"})
    assert one.physical_opens == 1, (
        f"«замок рівно раз» порушено: 5 повторів однієї команди → "
        f"{one.physical_opens} відмикань, а міра — рівно 1"
    )

    # 2) три РІЗНІ накази: дедуплікація не сміє глушити справжні команди
    many = LockController()
    for cid in ("cmd-43", "cmd-44", "cmd-45"):
        many.handle({"id": cid, "action": "open"})
    assert many.physical_opens == 3, (
        f"«замок рівно раз» порушено: 3 різні команди → "
        f"{many.physical_opens} відмикань, а мало бути 3"
    )
