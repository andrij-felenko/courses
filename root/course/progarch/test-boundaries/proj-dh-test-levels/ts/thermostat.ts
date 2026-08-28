// thermostat.ts — СИСТЕМА (те, що поїде в прод). Один код на всі три рівні.
export interface Sensor { read(): number; }        // контракт: завжди віддає °C
export interface Heater { on(): void; off(): void; }

// політика + проводка: читає крізь шов, керує грілкою
export function decide(sensor: Sensor, heater: Heater, threshold: number): void {
  if (sensor.read() < threshold) heater.on();
  else heater.off();
}

export interface Device { tempF(): number; }        // вендорів пристрій говорить у °F

// адаптер: вендорові °F → наші °C. Тут — правильна версія.
export class VendorSensorAdapter implements Sensor {
  constructor(private device: Device) {}
  read(): number {
    return (this.device.tempF() - 32) * 5 / 9;
  }
}

export type Config = { threshold: number };

// хаб: те, що прод збирає й крутить — справжній давач, справжня грілка, оберти
export class Hub {
  constructor(private sensor: Sensor, private heater: Heater,
              private threshold: number) {}
  tick(): void { decide(this.sensor, this.heater, this.threshold); }
  run(everyMs: number): void { setInterval(() => this.tick(), everyMs); }
}

// збірка: розв'язує конфіг у зібраний хаб (те саме, що кличе прод на старті)
export function buildHub(sensor: Sensor, heater: Heater, cfg: Config): Hub {
  return new Hub(sensor, heater, cfg.threshold);
}
