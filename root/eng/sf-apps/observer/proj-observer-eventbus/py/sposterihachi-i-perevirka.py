# Звичайне табло — просто показує числа (pull: саме бере з суб'єкта).
class CurrentDisplay:
    def update(self, station: "WeatherStation") -> None:
        r = station.reading
        print(f"Табло: {r.temp}°C, вологість {r.humidity}%")


# Табло, що падає, — імітуємо збій (мережа лягла, диск повний тощо).
class FlakyDisplay:
    def update(self, station: "WeatherStation") -> None:
        raise RuntimeError("не дотягнувся до сервера")


# Сигналізатор: спрацював один раз і сам відписався — ПРЯМО в update().
class OneShotAlarm:
    def __init__(self, station: "WeatherStation", limit: float) -> None:
        self._station = station
        self._limit = limit

    def update(self, station: "WeatherStation") -> None:
        if station.reading.temp > self._limit:
            print(f"🚨 Тривога: {station.reading.temp}°C > {self._limit}")
            self._station.unsubscribe(self)   # відписка в ході розсилки!


station = WeatherStation()
station.subscribe(CurrentDisplay())
station.subscribe(FlakyDisplay())               # цей кидатиме
station.subscribe(OneShotAlarm(station, 30))    # цей відпишеться

station.set_reading(35, 40)
# Табло: 35°C, вологість 40%
# (FlakyDisplay кинув — залоговано, розсилка НЕ обірвалась)
# 🚨 Тривога: 35°C > 30   ← і сигналізатор тут-таки відписався

station.set_reading(36, 41)
# Табло: 36°C, вологість 41%
# (Flaky знову кинув — знову пережили)
# тиша від сигналізатора — його вже нема в списку
