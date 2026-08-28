from enum import Enum

# Скільки часу між ударами й скільки пропусків терпимо — це НЕ константи
# «з голови», а прямий переклад сценарію доступності в числа:
#   BEAT_PERIOD_MS  — як часто головний зобов'язаний битися;
#   MISS_LIMIT      — скільки ударів підряд може пропасти, поки ми ще
#                     не оголошуємо смерть (це і є ГІСТЕРЕЗИС виявлення).
BEAT_PERIOD_MS = 500
MISS_LIMIT     = 3          # смерть визнаємо після ~1.5 с тиші


class Health(Enum):
    UP      = 0
    SUSPECT = 1
    DOWN    = 2


class NodeHealth:
    def __init__(self, now_ms: int):
        self.last_beat_ms = now_ms   # час останнього почутого удару
        self.missed = 0              # скільки періодів поспіль тиша
        self.health = Health.UP      # поточний присуд монітора

    # Прийшов фізичний удар від вузла — тиша скинута.
    def on_beat(self, now_ms: int) -> None:
        self.last_beat_ms = now_ms
        self.missed = 0
        self.health = Health.UP

    # Викликається періодично (напр., з таймера монітора). Рахує тишу
    # й підіймає присуд по щаблях UP -> SUSPECT -> DOWN.
    def tick(self, now_ms: int) -> None:
        if now_ms - self.last_beat_ms < BEAT_PERIOD_MS:
            return                       # удар устиг у вікно — усе гаразд

        # період минув без удару; зсуваємо «годинник очікування» на період,
        # щоб один пропуск рахувався один раз, а не безперервно
        self.last_beat_ms += BEAT_PERIOD_MS
        self.missed += 1

        if self.missed >= MISS_LIMIT:
            self.health = Health.DOWN
        else:
            self.health = Health.SUSPECT
