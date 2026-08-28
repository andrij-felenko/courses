// Подання — лише інтерфейс: команди екрана й сигнал про дотик. Ні слова про модель.
interface ThermostatView {
    void showTemperature(String text);   // презентер каже, ЩО показати
    void showColor(String hex);
    void onNudge(IntConsumer handler);    // екран лише доповідає «мене торкнули»
}

class ThermostatPresenter {
    private final ThermostatView view;
    private final Thermostat model;
    ThermostatPresenter(ThermostatView view, Thermostat model) {
        this.view = view; this.model = model;
        view.onNudge(this::nudge);        // підписатися на дотики екрана
    }
    private void nudge(int delta) {
        model.nudge(delta);               // 1. попросити модель змінитися (правило межі — в ній)
        int t = model.target();           // 2. прочитати свіжий результат
        view.showTemperature(t + "°");    // 3. власноруч розкласти на екран
        view.showColor(t > 24 ? "#c0392b" : "#2457d6");
    }
}

// Тест без жодного віджета: фальшиве подання просто запам'ятовує виклики.
var shown = new ArrayList<String>();
var press = new IntConsumer[1];
ThermostatView fake = new ThermostatView() {
    public void showTemperature(String t) { shown.add(t); }
    public void showColor(String hex) { }
    public void onNudge(IntConsumer h) { press[0] = h; }   // перехопити обробник
};
new ThermostatPresenter(fake, new Thermostat());   // модель стартує на 22°
press[0].accept(+1);                               // імітуємо дотик «+» — екрана не існує
assert shown.get(shown.size() - 1).equals("23°");  // презентер штовхнув «23°» у подання
