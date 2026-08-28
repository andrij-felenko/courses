# fake_device.py — фальшивий драйвер, що ЧЕСНО грає контракт.
# Не читає заліза; існує, щоб проти нього перевіряли хаб. Чеснота — тримати I-1..I-6.
import time
from device_driver import Reading, Ok, Err, Ack, Accepted, Celsius

class FakeDevice:
    def __init__(self, script=None):
        self._script = script or [21.4, "timeout", 22.0, "offline", 19.998]
        self._i = 0
        self._target: Celsius = 20.0
        self.writes = 0                       # лічильник фізичних записів — аудит, НЕ контракт

    def read(self) -> Reading:
        step = self._script[self._i % len(self._script)]
        self._i += 1
        if step in ("offline", "timeout"):
            return Err(reason=step)                     # I-3: збій — значення, не викид
        temp_c = min(85.0, max(-40.0, step))            # I-2: чесно затискає в межі
        return Ok(temp_c=temp_c, at=time.time())        # I-6: at у секундах

    def set_target(self, temp_c: Celsius) -> Ack:
        if temp_c == self._target:
            return Accepted()                           # I-4: уже там — не повторюємо запис
        self._target = temp_c
        self.writes += 1                                # фізичний запис стався рівно раз
        return Accepted()

    @property
    def target(self) -> Celsius:                        # аудитове вікно — НЕ контракт
        return self._target
