// Справжнє подання: тільки віджети. Ні арифметики, ні умов, ні складання рядків.
class ThermostatScreen implements ThermostatView {
  constructor(private readonly root: HTMLElement) {}

  private el<T extends HTMLElement>(cls: string): T {
    return this.root.querySelector<T>("." + cls)!;
  }

  showTemperature(text: string): void { this.el("temp").textContent = text; }
  showBarColor(hex: string): void     { this.el("bar").style.background = hex; }
  setMinusEnabled(on: boolean): void  { this.el<HTMLButtonElement>("minus").disabled = !on; }
  setPlusEnabled(on: boolean): void   { this.el<HTMLButtonElement>("plus").disabled = !on; }
  showStatus(text: string): void      { this.el("status").textContent = text; }

  onNudge(handler: (delta: number) => void): void {
    this.el("minus").addEventListener("click", () => handler(-1));
    this.el("plus").addEventListener("click", () => handler(+1));
  }
}
