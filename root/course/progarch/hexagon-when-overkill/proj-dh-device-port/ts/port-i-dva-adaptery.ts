// ПОРТ — давач і розетка одним отвором, мовою ядра
interface Device {
  temperature(): Promise<number>;   // °C, не мілі-градуси й не вольти
  heat(on: boolean): Promise<void>;
}

// ── Адаптер 1: СПРАВЖНІЙ. Єдиний в усьому хабі, хто говорить мовою заліза. ──
import { readFile } from "node:fs/promises";

class RealDevice implements Device {                 // 1-Wire давач + Wi-Fi розетка
  constructor(private w1: string, private plugUrl: string) {}

  async temperature(): Promise<number> {
    const text = await readFile(`/sys/bus/w1/devices/${this.w1}/w1_slave`, "utf8");
    const milli = parseInt(text.split("t=").pop()!, 10);  // DS18B20 → мілі-градуси
    return milli / 1000;                                  // → °C ТУТ, на межі
  }

  async heat(on: boolean): Promise<void> {
    await fetch(`${this.plugUrl}/relay/0?turn=${on ? "on" : "off"}`);
  }
}

// ── Адаптер 2: ПІДРОБКА. Кімната живе в пам'яті + пише журнал. ──
class FakeDevice implements Device {
  private room: number;
  private on = false;
  readonly log: boolean[] = [];       // журнал переходів для тесту

  constructor(start = 18.0) { this.room = start; }

  async temperature(): Promise<number> {
    this.room += (this.on ? 0.4 : -0.2) + (Math.random() - 0.5) * 0.1;
    return Math.round(this.room * 10) / 10;
  }

  async heat(on: boolean): Promise<void> {
    if (on !== this.on) this.log.push(on);   // лише реальні перемикання
    this.on = on;
  }
}
