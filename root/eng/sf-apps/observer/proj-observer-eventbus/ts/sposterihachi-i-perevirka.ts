// Звичайне табло — просто показує числа (pull: саме бере з суб'єкта).
class CurrentDisplay implements Observer {
  update(station: WeatherStation): void {
    const { temp, humidity } = station.reading;
    console.log(`Табло: ${temp}°C, вологість ${humidity}%`);
  }
}

// Табло, що падає, — імітуємо збій (мережа лягла, диск повний тощо).
class FlakyDisplay implements Observer {
  update(_: WeatherStation): void {
    throw new Error("не дотягнувся до сервера");
  }
}

// Сигналізатор: спрацював один раз і сам відписався — ПРЯМО в update().
class OneShotAlarm implements Observer {
  constructor(private station: WeatherStation, private limit: number) {}
  update(station: WeatherStation): void {
    if (station.reading.temp > this.limit) {
      console.log(`🚨 Тривога: ${station.reading.temp}°C > ${this.limit}`);
      this.station.unsubscribe(this);   // відписка в ході розсилки!
    }
  }
}

const station = new WeatherStation();
station.subscribe(new CurrentDisplay());
station.subscribe(new FlakyDisplay());              // цей кидатиме
station.subscribe(new OneShotAlarm(station, 30));   // цей відпишеться

station.setReading(35, 40);
// Табло: 35°C, вологість 40%
// (FlakyDisplay кинув — залоговано, розсилка НЕ обірвалась)
// 🚨 Тривога: 35°C > 30   ← і сигналізатор тут-таки відписався

station.setReading(36, 41);
// Табло: 36°C, вологість 41%
// (Flaky знову кинув — знову пережили)
// тиша від сигналізатора — його вже нема в списку
