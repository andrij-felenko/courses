// ── Модель: єдина, хто знає правило меж. Про екран — ані слова.
class Thermostat {
  static readonly MIN = 5;
  static readonly MAX = 30;
  private value = 22;

  get target(): number { return this.value; }

  nudge(delta: number): void {
    this.value = Math.max(Thermostat.MIN, Math.min(Thermostat.MAX, this.value + delta));
  }
}

// ── Контракт екрана: п'ять команд і один сигнал назовні.
interface ThermostatView {
  showTemperature(text: string): void;   // готовий рядок, не число
  showBarColor(hex: string): void;
  setMinusEnabled(on: boolean): void;
  setPlusEnabled(on: boolean): void;
  showStatus(text: string): void;
  onNudge(handler: (delta: number) => void): void;
}

const HOT = "#c0392b", COLD = "#2457d6", CALM = "#6b7280";

// ── Презентер: одна дорога до подання — render().
class ThermostatPresenter {
  constructor(
    private readonly view: ThermostatView,
    private readonly model: Thermostat,
  ) {}

  start(): void {
    this.view.onNudge(delta => {
      this.model.nudge(delta);   // межу обріже сама модель
      this.render();             // і одразу — свіжий кадр цілком
    });
    this.render();               // перший кадр малюємо самі, до будь-якого дотику
  }

  /** Увесь екран як функція від стану моделі. Інших шляхів до подання нема. */
  private render(): void {
    const t = this.model.target;
    this.view.showTemperature(`${t}°`);
    this.view.showBarColor(t > 24 ? HOT : t < 18 ? COLD : CALM);
    this.view.setMinusEnabled(t > Thermostat.MIN);
    this.view.setPlusEnabled(t < Thermostat.MAX);
    this.view.showStatus(
      t >= Thermostat.MAX ? `Вище не можна: ${t}°`
      : t <= Thermostat.MIN ? `Нижче не можна: ${t}°`
      : `Тримає ${t}°`);
  }
}
