// fake-device.ts — фальшивий драйвер, що ЧЕСНО грає контракт вище.
// Не читає заліза; існує, щоб проти нього перевіряли хаб. Чеснота — тримати I-1..I-6.
import type { DeviceDriver, Reading, Ack, Celsius, Fault } from "./device-driver.ts";

export class FakeDevice implements DeviceDriver {
  private i = 0;
  private targetC: Celsius = 20;
  writes = 0;                       // лічильник фізичних записів — для аудиту, НЕ контракт

  // сценарій: майбутнє tempC або збій; крутиться по колу
  constructor(
    private script: Array<Celsius | Fault> = [21.4, "timeout", 22, "offline", 19.998],
  ) {}

  async read(): Promise<Reading> {
    const step = this.script[this.i++ % this.script.length];
    if (step === "offline" || step === "timeout") {
      return { ok: false, reason: step };              // I-3: збій — ЗНАЧЕННЯ, не викид
    }
    const tempC = Math.min(85, Math.max(-40, step));   // I-2: чесно затискає в межі
    return { ok: true, tempC, at: Date.now() };        // I-6: at у МС
  }

  async setTarget(tempC: Celsius): Promise<Ack> {
    if (tempC === this.targetC) return { ok: true };   // I-4: уже там — запис НЕ повторюємо
    this.targetC = tempC;
    this.writes++;                                     // фізичний запис стався РІВНО раз
    return { ok: true };
  }

  get target(): Celsius { return this.targetC; }       // аудитове вікно у фейк — НЕ контракт
}
