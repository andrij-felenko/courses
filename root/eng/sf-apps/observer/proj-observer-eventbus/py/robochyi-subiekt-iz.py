from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
import logging

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Reading:
    temp: float
    humidity: float


class Observer(Protocol):
    def update(self, station: "WeatherStation") -> None: ...


class WeatherStation:
    def __init__(self) -> None:
        # Список у ПОРЯДКУ вставки: list, не set, — щоб порядок був
        # стабільний. Дублікати відсікаємо самі при subscribe.
        self._observers: list[Observer] = []
        self._reading = Reading(0.0, 0.0)
        self._notifying = False   # запобіжник від повторного входу
        self._dirty = False       # стан змінився під час розсилки

    def subscribe(self, o: Observer) -> None:
        if o not in self._observers:
            self._observers.append(o)

    def unsubscribe(self, o: Observer) -> None:
        try:
            self._observers.remove(o)
        except ValueError:
            pass  # не був підписаний — не біда

    def _notify(self) -> None:
        # 1. Прапорець реентрантності: якщо вже йде розсилка — не входимо
        #    вглиб, лише лишаємо мітку «є нові дані» й виходимо.
        if self._notifying:
            self._dirty = True
            return
        self._notifying = True
        try:
            # Зовнішній цикл добирає зміни, що накопичилися ПІД ЧАС розсилки.
            while True:
                self._dirty = False
                # 2. Копія списку: відписка/підписка з-під update() міняє
                #    self._observers, але не цей знімок — обхід не зламається.
                for o in list(self._observers):
                    # Пропускаємо тих, кого відписали в цій-таки розсилці.
                    if o not in self._observers:
                        continue
                    # 3. Ізоляція: чужий виняток не зриває розсилку решті.
                    try:
                        o.update(self)
                    except Exception:
                        log.exception("Спостерігач кинув виняток, пропускаю")
                if not self._dirty:
                    break  # ніхто не змінив стан у ході — виходимо
        finally:
            self._notifying = False  # ЗАВЖДИ знімаємо, навіть при збої

    # Публічний мутатор — єдині двері, крізь які стан змінюється.
    def set_reading(self, temp: float, humidity: float) -> None:
        self._reading = Reading(temp, humidity)
        self._notify()

    @property
    def reading(self) -> Reading:
        return self._reading  # frozen dataclass — віддати можна прямо
