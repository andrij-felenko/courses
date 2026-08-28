// doubles.ts
import type { Reading, Sensor, Heater } from "./home";

export class FakeSensor implements Sensor {   // фейк: віддає задані виміри, один за одним
  private q: Reading[];
  constructor(...readings: Reading[]) { this.q = readings; }
  read(): Reading {
    const r = this.q.shift();
    if (r === undefined) throw new Error("FakeSensor вичерпано");  // інакше — тихий undefined
    return r;
  }
}

export class SpyHeater implements Heater {    // шпигун: нічого не гріє, лише пам'ятає виклики
  calls: string[] = [];
  on()  { this.calls.push("on"); }
  off() { this.calls.push("off"); }
}
