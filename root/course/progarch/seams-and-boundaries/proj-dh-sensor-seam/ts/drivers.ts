// drivers.ts — справжні драйвери. Тіла мокують фізику; у продакшені — залізо.
import type { Sensor, Heater } from "./thermostat.ts";

export class Room {
  constructor(public temp = 18.0, public heating = false) {}
}

export class RealSensor implements Sensor {
  constructor(private readonly room: Room) {}
  read(): number {
    this.room.temp += (this.room.heating ? 0.4 : -0.2) + (Math.random() - 0.5) * 0.1;
    return Math.round(this.room.temp * 10) / 10;          // °C дробом — контракт
  }
}

export class RealHeater implements Heater {
  constructor(private readonly room: Room) {}
  on(): void {
    if (!this.room.heating) {                             // ідемпотентно
      this.room.heating = true;
      console.log("[розетка] обігрівач УВІМКНЕНО");
    }
  }
  off(): void {
    if (this.room.heating) {
      this.room.heating = false;
      console.log("[розетка] обігрівач вимкнено");
    }
  }
}

// main.ts — точка ввімкнення: тут вирішено, що під'єднати до шва.
import { decide } from "./thermostat.ts";
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function run(): Promise<void> {
  const room = new Room(18.0);
  const sensor = new RealSensor(room), heater = new RealHeater(room);   // ← вимикач ТУТ
  while (true) {
    decide(sensor, heater, 20.0);                                        // політику не чіпаємо
    await sleep(30_000);
  }
}
run();
