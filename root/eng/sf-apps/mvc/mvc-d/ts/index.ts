class Thermostat {                    // МОДЕЛЬ: дані + правило, і нічого про екран
  private _target = 22;
  private observers: (() => void)[] = [];   // хто хоче знати — не знаю хто саме

  get target() { return this._target; }

  nudge(delta: number) {              // правило предметної області живе тут
    this._target = Math.max(5, Math.min(30, this._target + delta));
    for (const notify of this.observers) notify();  // сповістити залежних
  }

  onChange(fn: () => void) { this.observers.push(fn); }
}
