# ── 4. Прогін: «нікого немає» з одним офлайн-замком ──

class FakeGateway:                      # макет заліза: знає, хто на зв'язку
    def __init__(self, online: set[str]):
        self._online = online
    def bring_online(self, id: str) -> None:
        self._online.add(id)
    def send_lock(self, id: DeviceId) -> LockOutcome:
        if id.value not in self._online:
            return Offline()            # у житті тут таймаут Wi-Fi, черга команд
        return Acked(LockState.LOCKED)


home_id = HomeId("h-1")
home = Home(home_id, UserId("u-owner"))
hall = RoomId("hall")
home.add_room(hall)

door_names = ["front","back","garage","balcony","cellar","gate","patio","side","roof","shed"]
locks: dict[str, Lock] = {}
for name in door_names:
    dev = DeviceId(name)
    home.attach_lock(dev)
    locks[name] = Lock(dev, home_id, Location(hall, name))

# Гараж — офлайн. Решта дев'ять — на зв'язку.
gateway = FakeGateway({n for n in door_names if n != "garage"})
reconciler = AwayReconciler(gateway)

# Власник тисне «йдемо»: дім ставить БАЖАНИЙ режим — і тільки. Це одна транзакція.
home.set_mode(HomeMode.AWAY)

# Прохід 1: дев'ять замкнулися, гараж мовчить.
r1 = reconciler.sweep(home, locks)
print("прохід 1:", r1, "· зведено:", r1.settled)
print("гараж зараз:", locks["garage"].current.value)

# ...згодом гараж повертається на зв'язок. Повторюємо — доганяємо решту.
gateway.bring_online("garage")
r2 = reconciler.sweep(home, locks)
print("прохід 2:", r2, "· зведено:", r2.settled)
print("гараж зараз:", locks["garage"].current.value)
