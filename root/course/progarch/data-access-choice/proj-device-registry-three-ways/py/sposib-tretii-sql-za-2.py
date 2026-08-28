class InMemoryDeviceRepository:          # той самий інтерфейс, жодного рядка SQL
    def __init__(self):
        self._items, self._next = {}, 1
    def save(self, d):
        if d.id is None:
            d.id, self._next = self._next, self._next + 1
        self._items[d.id] = d
    def find(self, id):
        return self._items.get(id)
    def find_silent_over(self, minutes):     # логіка в пам'яті — тесту досить
        return [d for d in self._items.values() if d.last_seen is None]

def audit_silent(repo: DeviceRepository, minutes: int):   # сервіс знає лише інтерфейс
    return repo.find_silent_over(minutes)

def test_audit_swaps_the_boundary():
    repo = InMemoryDeviceRepository()
    repo.save(Device("lamp", "hall", last_seen=None))       # мовчить
    repo.save(Device("lock", "entrance", last_seen=9_000))  # озвався
    assert len(audit_silent(repo, minutes=60)) == 1
