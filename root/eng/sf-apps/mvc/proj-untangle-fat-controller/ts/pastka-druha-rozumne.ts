// ПАСТКА — розумне подання: у читача залізла логіка й навіть запис у модель
class BarView {
  render(): void {
    let t = this.model.target;
    if (t > 28) t = 28;                          // ← подання САМО «підправляє» число
    if (this.model.target >= Thermostat.MAX) {   // ← подання ВИРІШУЄ політику
      this.model.nudge(-1);                      // ← і МІНЯЄ модель — читач став писарем
    }
    const span = Thermostat.MAX - Thermostat.MIN;
    const filled = Math.round((t - Thermostat.MIN) / span * 20);
    console.log("  " + "█".repeat(filled) + "·".repeat(20 - filled));
  }
}
