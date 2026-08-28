// Модель подання: стан екрана звичайним об'єктом, про подання не знає
class ThermostatVM {
  private _t = 22;
  get temperature() { return this._t; }
  set temperature(v: number) {
    this._t = Math.min(30, Math.max(5, v));   // правило межі — тут
    this.changed();                           // сигнал рушієві зв'язування
  }
  get canSave() { return this._t >= 5 && this._t <= 30; }  // ознака для кнопки
  save = () => this.store.persist(this._t);   // дія-команда
  // changed() сповіщає підписників; посилань на поле чи кнопку — жодного
}
