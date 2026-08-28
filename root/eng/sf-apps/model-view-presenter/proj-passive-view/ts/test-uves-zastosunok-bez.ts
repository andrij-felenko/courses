// ── Фальшиве подання: не малює нічого, лише тримає останній кадр.
class FakeView implements ThermostatView {
  temp = ""; color = ""; status = "";
  minusEnabled = true; plusEnabled = true;
  press: (delta: number) => void = () => { throw new Error("ніхто не підписався на дотики"); };

  showTemperature(text: string) { this.temp = text; }
  showBarColor(hex: string)     { this.color = hex; }
  setMinusEnabled(on: boolean)  { this.minusEnabled = on; }
  setPlusEnabled(on: boolean)   { this.plusEnabled = on; }
  showStatus(text: string)      { this.status = text; }
  onNudge(handler: (delta: number) => void) { this.press = handler; }
}

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error("не збіглося: " + what);
}

function screenUnderTest(): FakeView {
  const view = new FakeView();
  new ThermostatPresenter(view, new Thermostat()).start();
  return view;
}

// 1. Кадр існує ще до першого дотику.
{
  const v = screenUnderTest();
  check(v.temp === "22°", "перший напис");
  check(v.status === "Тримає 22°", "перший рядок стану");
  check(v.plusEnabled && v.minusEnabled, "обидві кнопки живі посередині шкали");
}

// 2. Один дотик веде ввесь кадр, а не саму цифру.
{
  const v = screenUnderTest();
  v.press(+1);
  check(v.temp === "23°", "напис після «+»");
  check(v.color === CALM, "колір у спокійній зоні");
  check(v.status === "Тримає 23°", "рядок стану після «+»");
}

// 3. Стеля: модель не пускає далі, кнопка гасне, рядок стану міняє тон.
{
  const v = screenUnderTest();
  for (let i = 0; i < 20; i++) v.press(+1);   // 22 → 30, а далі нікуди
  check(v.temp === "30°", "напис на стелі");
  check(v.plusEnabled === false, "«+» на стелі згасла");
  check(v.minusEnabled === true, "«−» на стелі жива");
  check(v.status === "Вище не можна: 30°", "рядок стану на стелі");
  check(v.color === HOT, "колір на стелі");
}

console.log("усі перевірки пройшли — жодного віджета не створено");
