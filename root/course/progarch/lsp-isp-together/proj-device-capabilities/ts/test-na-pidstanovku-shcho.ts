// Крихітний раннер без залежностей — запускається як є.
let failures = 0;
function check(name: string, fn: () => void): void {
  try { fn(); console.log(`ok    ${name}`); }
  catch (e) { failures++; console.log(`FAIL  ${name}: ${(e as Error).message}`); }
}
function assert(cond: boolean, msg: string): void {
  if (!cond) throw new Error(msg);
}

// Контракт Switchable — придатний для БУДЬ-ЯКОЇ реалізації.
function switchableContract(make: () => Switchable): void {
  const d = make();
  d.turnOn();  assert(d.isOn() === true,  "після turnOn має бути ввімкнено");
  d.turnOff(); assert(d.isOn() === false, "після turnOff має бути вимкнено");
}

// Об'єкт, що ВДАЄ Switchable: форма збігається, а поведінка бреше —
// точно та пастка, яку товстий IDevice робив неминучою.
class LyingSwitch implements Switchable {
  turnOn():  void    { throw new Error("не вмикається"); }
  turnOff(): void    { throw new Error("не вимикається"); }
  isOn():    boolean { return false; }
}

check("nightMode не падає на змішаному парку", () =>
  nightMode([new TempSensor(19), new SmartSocket(), new DoorLock(), new Camera()]));

check("SmartSocket чесно виконує контракт Switchable", () =>
  switchableContract(() => new SmartSocket()));

check("сторож ПРОПУСКАЄ брехуна за формою", () =>
  assert(isSwitchable(new LyingSwitch()) === true, "форма Switchable у нього є"));

check("а контракт брехуна ЛОВИТЬ", () => {
  let caught = false;
  try { switchableContract(() => new LyingSwitch()); } catch { caught = true; }
  assert(caught, "контракт мусив упіймати брехню, але пропустив");
});

console.log(failures ? `\n${failures} впало` : "\nусе зелене");
