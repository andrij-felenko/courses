import * as fs from "node:fs";

class FileStore {
  constructor(private readonly model: Thermostat, private readonly path: string) {
    model.onChange(() => this.save());   // той самий сигнал, що й у подань
  }

  private save(): void {
    fs.writeFileSync(this.path, String(this.model.target));
  }
}

// ── збірка: усе сходиться на одній моделі ──
const model = new Thermostat(22);
const digit = new DigitView(model);              // підписник 1
const bar   = new BarView(model);                // підписник 2
const store = new FileStore(model, "target.txt"); // підписник 3
const controller = new ThermostatController(model);

controller.plusClicked();   // 22 → 23: обидва подання перемалювались, файл записався
