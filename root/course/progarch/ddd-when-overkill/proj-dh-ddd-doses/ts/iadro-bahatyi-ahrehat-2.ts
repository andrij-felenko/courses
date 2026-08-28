class Room {
  private heating = false;
  private cooling = false;
  private lightsOn = false;
  private targetC = 21;

  constructor(readonly name: string) {}

  // Сценарій — цілісний стан, а не приріст до старого. Лише через корінь.
  apply(scenario: Scenario): void {
    this.stopClimate();                                   // новий сценарій починає з чистого
    const c = scenario.climate;
    if (c.want === "heat")      this.startHeating(c.targetC);
    else if (c.want === "cool") this.startCooling(c.targetC);
    this.lightsOn = scenario.lightsOn;
  }

  startHeating(targetC: number): void {
    this.changeClimate(true, this.cooling);               // хочу гріти, кулер лишаю як є
    this.targetC = targetC;
  }
  startCooling(targetC: number): void {
    this.changeClimate(this.heating, true);
    this.targetC = targetC;
  }
  stopClimate(): void {
    this.changeClimate(false, false);
  }

  // Інваріант безпеки живе ТУТ — в одному захищеному місці, і ніде більше.
  // Перевірка ПЕРЕД зміною: відмова не лишає кімнату в напівстані.
  private changeClimate(heating: boolean, cooling: boolean): void {
    if (heating && cooling)
      throw new DomainError(
        `${this.name}: обігрівач і кондиціонер не працюють у кімнаті разом`);
    this.heating = heating;
    this.cooling = cooling;
  }

  get climate(): "heating" | "cooling" | "idle" {
    if (this.heating) return "heating";
    if (this.cooling) return "cooling";
    return "idle";
  }
}
