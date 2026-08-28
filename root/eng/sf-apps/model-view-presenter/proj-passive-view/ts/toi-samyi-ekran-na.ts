// Модель тепер сама повідомляє про зміну — без цього прив'язки не буває.
class ObservableThermostat extends Thermostat {
  private readonly listeners: Array<() => void> = [];

  onChange(listener: () => void): void { this.listeners.push(listener); }

  nudge(delta: number): void {
    const before = this.target;
    super.nudge(delta);
    if (this.target !== before) this.listeners.forEach(fn => fn());
  }
}

// Контракт екрана схуд: цифру презентер більше не диктує.
interface SupervisedView {
  showBarColor(hex: string): void;
  setMinusEnabled(on: boolean): void;
  setPlusEnabled(on: boolean): void;
  showStatus(text: string): void;
  onNudge(handler: (delta: number) => void): void;
}

// Подання само тримає ниточку від числа моделі до напису.
class BoundThermostatScreen extends ThermostatScreen implements SupervisedView {
  constructor(root: HTMLElement, model: ObservableThermostat) {
    super(root);
    const paint = () => this.showTemperature(`${model.target}°`);
    model.onChange(paint);
    paint();
  }
}

// Презентер лишає собі тільки те, де є що вирішувати.
class SupervisingController {
  constructor(
    private readonly view: SupervisedView,
    private readonly model: Thermostat,
  ) {}

  start(): void {
    this.view.onNudge(delta => { this.model.nudge(delta); this.render(); });
    this.render();
  }

  private render(): void {
    const t = this.model.target;
    this.view.showBarColor(t > 24 ? HOT : t < 18 ? COLD : CALM);
    this.view.setMinusEnabled(t > Thermostat.MIN);
    this.view.setPlusEnabled(t < Thermostat.MAX);
    this.view.showStatus(
      t >= Thermostat.MAX ? `Вище не можна: ${t}°`
      : t <= Thermostat.MIN ? `Нижче не можна: ${t}°`
      : `Тримає ${t}°`);
  }
}
