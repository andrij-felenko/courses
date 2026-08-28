// Подання — лише інтерфейс: команди екрана й сигнал про дотик. Ні слова про модель.
interface ThermostatView {
  showTemperature(text: string): void;              // презентер каже, ЩО показати
  showColor(hex: string): void;
  onNudge(handler: (delta: number) => void): void;  // екран лише доповідає «мене торкнули»
}

class ThermostatPresenter {
  constructor(private view: ThermostatView, private model: Thermostat) {
    view.onNudge(delta => this.nudge(delta));        // підписатися на дотики екрана
  }
  private nudge(delta: number) {
    this.model.nudge(delta);                         // 1. попросити модель змінитися (правило межі — в ній)
    const t = this.model.target;                     // 2. прочитати свіжий результат
    this.view.showTemperature(`${t}°`);              // 3. власноруч розкласти на екран
    this.view.showColor(t > 24 ? "#c0392b" : "#2457d6");
  }
}

// Тест без жодного віджета: фальшиве подання просто запам'ятовує виклики.
let press: (d: number) => void = () => {};
const shown: string[] = [];
const fake: ThermostatView = {
  showTemperature: t => shown.push(t),
  showColor: () => {},
  onNudge: h => { press = h; },        // перехопити обробник, щоб «натиснути» з тесту
};
new ThermostatPresenter(fake, new Thermostat());  // модель стартує на 22°
press(+1);                                        // імітуємо дотик «+» — екрана не існує
console.assert(shown.at(-1) === "23°");           // презентер справді штовхнув «23°» у подання
