private render(): void {
  const t = this.model.target;
  this.view.showTemperature(`${t}°`);
  this.view.showBarColor(t > 24 ? HOT : t < 18 ? COLD : CALM);
  this.view.setMinusEnabled(!this.busy && t > Thermostat.MIN);
  this.view.setPlusEnabled(!this.busy && t < Thermostat.MAX);
  this.view.showStatus(
    this.busy ? "Надсилаю…"
    : this.error ?? (t >= Thermostat.MAX ? `Вище не можна: ${t}°`
                   : t <= Thermostat.MIN ? `Нижче не можна: ${t}°`
                   : `Тримає ${t}°`));
}
