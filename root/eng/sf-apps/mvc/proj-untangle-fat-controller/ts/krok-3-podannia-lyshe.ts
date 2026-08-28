class DigitView {
  constructor(private readonly model: Thermostat) {
    model.onChange(() => this.render());   // підписатися на сигнал зміни
    this.render();                         // намалюватися одразу
  }

  render(): void {
    console.log(`  ${this.model.target}°`);
  }
}

class BarView {
  constructor(private readonly model: Thermostat) {
    model.onChange(() => this.render());
    this.render();
  }

  render(): void {
    const t = this.model.target;
    const span = Thermostat.MAX - Thermostat.MIN;
    const filled = Math.round((t - Thermostat.MIN) / span * 20);
    console.log("  " + "█".repeat(filled) + "·".repeat(20 - filled));
  }
}
