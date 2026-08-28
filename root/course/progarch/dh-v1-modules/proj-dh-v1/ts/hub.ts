// hub.ts — Digital Homes v1: той самий дім, але за швами. Драйвери — мокові.

// ── Значення на межах: одиниця й статус живуть у типі, не в чиїйсь голові ──
interface Reading {
  readonly celsius: number;   // ЗАВЖДИ °C
  readonly ok: boolean;       // чи це справжнє свіже число
}
interface Config { readonly threshold: number; }   // поріг — вхід рішення
type Command = "HEAT" | "IDLE";                     // рішення — це ЗНАЧЕННЯ

// ── Порти: логіка залежить від них, а не від марки заліза ──
interface Sensor { read(): Reading; }
interface Heater { on(): void; off(): void; }       // on/off — ідемпотентні

// ── Мокова фізика: те єдине, що справді спільне — повітря кімнати ──
class MockRoom {
  temp: number;
  heating = false;
  constructor(temp = 18.0) { this.temp = temp; }
  drift(): void {             // холоне сама, гріється під струмом, + шум виміру
    this.temp += (this.heating ? 0.4 : -0.2) + (Math.random() - 0.5) * 0.1;
  }
}

// ── Драйвер давача: мову СВОГО заліза знає тільки він ──
class MockThermometer implements Sensor {
  private i = 0;
  constructor(private room: MockRoom, private faults: number[] = []) {}
  read(): Reading {
    this.room.drift();                         // фізика марширує далі, дарма що давач німий
    if (this.faults[this.i++]) return { celsius: NaN, ok: false };  // збій → «не вірю»
    const milli = Math.round(this.room.temp * 1000);   // сирий діалект: цілі мілі-°C, як 1-Wire
    return { celsius: milli / 1000, ok: true };        // переклад одиниць ТУТ, на краю
  }
}

// ── Драйвер розетки: ідемпотентний ──
class MockPlug implements Heater {
  constructor(private room: MockRoom, private name = "вітальня") {}
  on(): void {
    if (!this.room.heating) {                  // повторний «увімкни» реле дарма не смикає
      this.room.heating = true;
      console.log(`[${this.name}] обігрівач УВІМКНЕНО`);
    }
  }
  off(): void {
    if (this.room.heating) {
      this.room.heating = false;
      console.log(`[${this.name}] обігрівач вимкнено`);
    }
  }
}

// ── Чисте рішення: ті самі входи → той самий вихід, жодних ефектів ──
function decide(r: Reading, cfg: Config): Command {
  if (!r.ok) return "IDLE";                    // давач мовчить → безпечний спокій
  return r.celsius < cfg.threshold ? "HEAT" : "IDLE";
}

// ── Збірка: тонкий цикл, що лише диригує ──
const sleep = (ms: number) => new Promise((res) => setTimeout(res, ms));

async function run(sensor: Sensor, heater: Heater, cfg: Config, ticks = Infinity) {
  for (let n = 0; n < ticks; n++) {
    const reading = sensor.read();             // драйвер ховає діалект і збої заліза
    if (!reading.ok) console.log("[давач] мовчить — тримаю безпечний спокій");
    if (decide(reading, cfg) === "HEAT") heater.on();
    else heater.off();
    await sleep(30_000);
  }
}

// ── Корінь склеювання: конкретне зустрічає конкретне рівно тут ──
const room = new MockRoom(18.0);               // спільне «повітря» для давача й розетки
run(new MockThermometer(room), new MockPlug(room), { threshold: 20.0 });
