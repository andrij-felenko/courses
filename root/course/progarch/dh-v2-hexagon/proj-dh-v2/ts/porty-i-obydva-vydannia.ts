// ── Порти: застосунок залежить від них, а не від марки заліза ──
interface Sensor { read(): Reading; }
interface Heater { on(): void; off(): void; }          // on/off — ідемпотентні
interface DeviceRepository { save(d: Device): void; all(): Device[]; }

// ── Справжні адаптери: єдині, хто говорить мовою заліза ──
import { readFileSync } from "node:fs";

class OneWireThermometer implements Sensor {           // DS18B20 по 1-Wire
  constructor(private w1Id: string) {}
  read(): Reading {
    try {
      const text = readFileSync(`/sys/bus/w1/devices/${this.w1Id}/w1_slave`, "utf8");
      const milli = parseInt(text.split("t=").pop()!, 10);   // мілі-градуси
      return { celsius: milli / 1000, ok: true };            // переклад ТУТ, на краю
    } catch {
      return { celsius: NaN, ok: false };                    // німий давач → «не вірю»
    }
  }
}

class SmartPlug implements Heater {                    // Wi-Fi розетка (Shelly)
  private on_ = false;
  constructor(private url: string) {}
  on():  void { if (!this.on_) { this.toggle("on");  this.on_ = true;  } }
  off(): void { if (this.on_)  { this.toggle("off"); this.on_ = false; } }
  private toggle(turn: string): void { void fetch(`${this.url}/relay/0?turn=${turn}`); }
}

// ── Підробки: кожен порт має свою, дім живе в пам'яті ──
class FakeSensor implements Sensor {                   // віддає задану температуру
  celsius = 18.0;
  ok = true;
  constructor(celsius = 18.0) { this.celsius = celsius; }   // тест крутить поля, граючи сценарій
  read(): Reading { return { celsius: this.celsius, ok: this.ok }; }
}

class FakeHeater implements Heater {                   // журнал перемикань, без реле
  private on_ = false;
  readonly log: boolean[] = [];
  on():  void { if (!this.on_) { this.on_ = true;  this.log.push(true);  } }   // лише реальні зміни
  off(): void { if (this.on_)  { this.on_ = false; this.log.push(false); } }
}

class InMemoryDeviceRepository implements DeviceRepository {   // реєстр у пам'яті
  private items: Device[] = [];
  save(d: Device): void { this.items.push(d); }
  all(): Device[] { return [...this.items]; }
}
