# Табло-«стабілізатор»: якщо температура непарна — підправляє на парну.
# Це змінює стан станції ПРЯМО в update() → рекурсивний notify().
class Stabilizer:
    def update(self, station: "WeatherStation") -> None:
        t = station.reading.temp
        if t % 2 != 0:
            print(f"Стабілізатор: {t} → {t + 1}")
            station.set_reading(t + 1, station.reading.humidity)  # повторний вхід!


s = WeatherStation()
s.subscribe(CurrentDisplay())
s.subscribe(Stabilizer())

s.set_reading(21, 50)
# Стабілізатор: 21 → 22        ← спробував змінити стан у ході розсилки
# Табло: 22°C, вологість 50%   ← але сповіщення пройшло РІВНО раз, парним 22
