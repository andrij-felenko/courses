interface Observer {
  update(subject: WeatherStation): void;   // суб'єкт викличе це при зміні
}

class WeatherStation {                      // СУБ'ЄКТ
  private observers = new Set<Observer>();  // список підписників
  private _temp = 0;

  subscribe(o: Observer)   { this.observers.add(o); }
  unsubscribe(o: Observer) { this.observers.delete(o); }

  private notify() {                        // серце патерна
    for (const o of this.observers) o.update(this);
  }

  setTemp(t: number) {                      // ось тут стан змінюється
    this._temp = t;
    this.notify();                          // ...і одразу летить сигнал
  }
  get temp() { return this._temp; }
}

class Display implements Observer {         // конкретний СПОСТЕРІГАЧ
  update(station: WeatherStation) {
    console.log(`Табло: ${station.temp}°C`);
  }
}
