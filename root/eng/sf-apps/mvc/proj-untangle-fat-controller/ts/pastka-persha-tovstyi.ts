// ПАСТКА — товстий контролер: у переклад вводу знову залізли правило, читання екрана, рендер і запис
class ThermostatController {
  plusClicked(): void {
    let t = this.digitView.readNumber();  // ← читає стан З ЕКРАНА, не з моделі
    if (t < 30) t += 1;                   // ← ПРАВИЛО межі — знову тут!
    this.model.setTarget(t);              // ← модель зведена до сетера-мішка
    this.barView.redraw(t);               // ← контролер сам МАЛЮЄ
    this.store.save(t);                   // ← і сам ЗБЕРІГАЄ
  }
}
