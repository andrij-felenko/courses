import java.util.function.IntConsumer;

// ── Модель: єдина, хто знає правило меж. Про екран — ані слова.
final class Thermostat {
    static final int MIN = 5, MAX = 30;
    private int value = 22;

    int target() { return value; }

    void nudge(int delta) {
        value = Math.max(MIN, Math.min(MAX, value + delta));
    }
}

// ── Контракт екрана: п'ять команд і один сигнал назовні.
interface ThermostatView {
    void showTemperature(String text);   // готовий рядок, не число
    void showBarColor(String hex);
    void setMinusEnabled(boolean on);
    void setPlusEnabled(boolean on);
    void showStatus(String text);
    void onNudge(IntConsumer handler);
}

// ── Презентер: одна дорога до подання — render().
final class ThermostatPresenter {
    static final String HOT = "#c0392b", COLD = "#2457d6", CALM = "#6b7280";

    private final ThermostatView view;
    private final Thermostat model;

    ThermostatPresenter(ThermostatView view, Thermostat model) {
        this.view = view;
        this.model = model;
    }

    void start() {
        view.onNudge(delta -> {
            model.nudge(delta);   // межу обріже сама модель
            render();             // і одразу — свіжий кадр цілком
        });
        render();                 // перший кадр малюємо самі, до будь-якого дотику
    }

    /** Увесь екран як функція від стану моделі. Інших шляхів до подання нема. */
    private void render() {
        int t = model.target();
        view.showTemperature(t + "°");
        view.showBarColor(t > 24 ? HOT : t < 18 ? COLD : CALM);
        view.setMinusEnabled(t > Thermostat.MIN);
        view.setPlusEnabled(t < Thermostat.MAX);
        view.showStatus(t >= Thermostat.MAX ? "Вище не можна: " + t + "°"
                      : t <= Thermostat.MIN ? "Нижче не можна: " + t + "°"
                      : "Тримає " + t + "°");
    }
}
