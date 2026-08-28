// device-actor.ts — один актор на пристрій: скринька + серійна обробка + ізольований стан
import { Frame } from "./core";

class DeviceActor {
  private mailbox: Frame[] = [];       // ШОВ А: єдина щілина в актора
  private draining = false;
  private state = { ewma: 0 };         // стан-автомат; назовні невидимий

  constructor(readonly id: string, private readonly onAnomaly: (f: Frame) => void) {}

  post(f: Frame): void {               // ядро кладе кадр — і вертається на смугу
    this.mailbox.push(f);
    if (!this.draining) { this.draining = true; setImmediate(() => this.drain()); }
  }

  private drain(): void {              // один споживач: по кадру за такт циклу
    const f = this.mailbox.shift();
    if (f === undefined) { this.draining = false; return; }
    this.step(f);
    setImmediate(() => this.drain()); // поступаємось смузі між кадрами — не тримаємо її
  }

  private step(f: Frame): void {       // дешевий крок: ковзне середнє + позначка стрибка
    this.state.ewma = this.state.ewma === 0 ? f.value : 0.9 * this.state.ewma + 0.1 * f.value;
    if (Math.abs(f.value - this.state.ewma) > 0.5 * this.state.ewma) this.onAnomaly(f);
  }
}
