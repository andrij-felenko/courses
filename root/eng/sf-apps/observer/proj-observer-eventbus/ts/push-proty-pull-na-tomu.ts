// PUSH-варіант: суб'єкт штовхає готові дані в аргумент.
interface PushObserver {
  update(reading: Reading): void;   // отримує ДАНІ, не суб'єкт
}

class PushStation {
  private observers: PushObserver[] = [];
  private _reading: Reading = { temp: 0, humidity: 0 };
  // (прапорці й копія списку — так само, як вище; тут опущено для стислості)

  subscribe(o: PushObserver): void {
    if (!this.observers.includes(o)) this.observers.push(o);
  }

  private notify(): void {
    const payload = this._reading;          // конверт події
    for (const o of this.observers.slice()) {
      try { o.update(payload); }            // дані летять В аргументі
      catch (err) { console.error(err); }
    }
  }

  setReading(temp: number, humidity: number): void {
    this._reading = { temp, humidity };
    this.notify();
  }
}

class PushDisplay implements PushObserver {
  update(reading: Reading): void {          // бере, що дали, нічого не питає
    console.log(`Табло: ${reading.temp}°C`);
  }
}
