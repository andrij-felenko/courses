// doubles.ts — те, що вішаємо ЗОВНІ розрізу
export class FakeSensor implements Sensor {          // фейк: віддає задане число (у °C)
  constructor(private celsius: number) {}
  read(): number { return this.celsius; }
}
export class SpyHeater implements Heater {           // шпигун: не гріє, лише пам'ятає стан
  isOn = false;
  on()  { this.isOn = true; }
  off() { this.isOn = false; }
}
export class FakeDevice implements Device {          // фейк вендорового пристрою — у °F
  constructor(private opts: { tempF: number }) {}
  tempF(): number { return this.opts.tempF; }
}
