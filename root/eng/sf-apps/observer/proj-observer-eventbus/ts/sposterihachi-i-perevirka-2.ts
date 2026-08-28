// Табло-«стабілізатор»: якщо температура непарна — підправляє її на парну.
// Це змінює стан станції ПРЯМО в update() → рекурсивний notify().
class Stabilizer implements Observer {
  update(station: WeatherStation): void {
    const t = station.reading.temp;
    if (t % 2 !== 0) {
      console.log(`Стабілізатор: ${t} → ${t + 1}`);
      station.setReading(t + 1, station.reading.humidity); // повторний вхід!
    }
  }
}

const s = new WeatherStation();
s.subscribe(new CurrentDisplay());
s.subscribe(new Stabilizer());

s.setReading(21, 50);
// Стабілізатор: 21 → 22        ← спробував змінити стан у ході розсилки
// Табло: 22°C, вологість 50%   ← але сповіщення пройшло РІВНО раз, парним 22
