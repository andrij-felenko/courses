class FakeRepo:                              # заступник бази: реєстр у пам'яті + лічильник читань
    def __init__(self):
        self._reg, self._state, self.reads = {}, {}, 0
    def seed(self, reg: HomeRegistry):
        self._reg[reg.home_id] = reg
    async def load_registry(self, home_id):
        self.reads += 1                       # ← скільки читань дійшло до «бази»
        await asyncio.sleep(0)                # вдаємо мережеву затримку, щоб закликання мало що стискати
        return self._reg[home_id]
    async def load_state(self, device_id):
        return self._state.get(device_id, LiveState(device_id, False, 0.0))
    async def rename_device(self, home_id, device_id, name):
        r = self._reg[home_id]
        self._reg[home_id] = HomeRegistry(home_id, r.plan, r.threshold,
            [Device(d.id, name if d.id == device_id else d.name, d.room, d.kind) for d in r.devices])
    async def pair_device(self, home_id, d):
        r = self._reg[home_id]
        self._reg[home_id] = HomeRegistry(home_id, r.plan, r.threshold, [*r.devices, d])

def sample():
    return HomeRegistry("home-42", "free", 20.0,
                        [Device("lock-1", "двері", "передпокій", "lock"),
                         Device("therm-7", "термостат", "вітальня", "thermostat")])
