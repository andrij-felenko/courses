import java.util.function.IntConsumer;

// ── Фальшиве подання: не малює нічого, лише тримає останній кадр.
final class FakeView implements ThermostatView {
    String temp = "", color = "", status = "";
    boolean minusEnabled = true, plusEnabled = true;
    IntConsumer press = d -> { throw new IllegalStateException("ніхто не підписався на дотики"); };

    public void showTemperature(String text) { temp = text; }
    public void showBarColor(String hex)     { color = hex; }
    public void setMinusEnabled(boolean on)  { minusEnabled = on; }
    public void setPlusEnabled(boolean on)   { plusEnabled = on; }
    public void showStatus(String text)      { status = text; }
    public void onNudge(IntConsumer handler) { press = handler; }
}

final class PassiveViewDemo {
    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("не збіглося: " + what);
    }

    static FakeView screenUnderTest() {
        FakeView view = new FakeView();
        new ThermostatPresenter(view, new Thermostat()).start();
        return view;
    }

    public static void main(String[] args) {
        // 1. Кадр існує ще до першого дотику.
        FakeView v1 = screenUnderTest();
        check("22°".equals(v1.temp), "перший напис");
        check("Тримає 22°".equals(v1.status), "перший рядок стану");
        check(v1.plusEnabled && v1.minusEnabled, "обидві кнопки живі посередині шкали");

        // 2. Один дотик веде ввесь кадр, а не саму цифру.
        FakeView v2 = screenUnderTest();
        v2.press.accept(+1);
        check("23°".equals(v2.temp), "напис після «+»");
        check(ThermostatPresenter.CALM.equals(v2.color), "колір у спокійній зоні");
        check("Тримає 23°".equals(v2.status), "рядок стану після «+»");

        // 3. Стеля: модель не пускає далі, кнопка гасне, рядок стану міняє тон.
        FakeView v3 = screenUnderTest();
        for (int i = 0; i < 20; i++) v3.press.accept(+1);   // 22 → 30, а далі нікуди
        check("30°".equals(v3.temp), "напис на стелі");
        check(!v3.plusEnabled, "«+» на стелі згасла");
        check(v3.minusEnabled, "«−» на стелі жива");
        check("Вище не можна: 30°".equals(v3.status), "рядок стану на стелі");
        check(ThermostatPresenter.HOT.equals(v3.color), "колір на стелі");

        System.out.println("усі перевірки пройшли — жодного віджета не створено");
    }
}
