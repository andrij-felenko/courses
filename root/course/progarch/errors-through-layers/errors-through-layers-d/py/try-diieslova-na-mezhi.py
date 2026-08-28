class SensorUnavailable(Exception):
    def __init__(self, room):
        super().__init__(f"давач у кімнаті «{room}» недоступний")
        self.room = room

def read_temp(room):                      # драйвер говорить мовою домену
    last = None
    for _ in range(2):                    # одна повторна спроба
        try:
            return i2c_read(room)         # може кинути I2CReadError
        except I2CReadError as e:
            last = e
    raise SensorUnavailable(room) from last   # переклали, зберігши причину (from)

# політика:
for room in rooms:
    try:
        t = read_temp(room)
    except SensorUnavailable as e:
        log.warning("тримаю стан: %s", e)     # лог РАЗ, саме тут
        continue                              # обігрівач цієї кімнати не чіпаємо
    apply_policy(room, t)
