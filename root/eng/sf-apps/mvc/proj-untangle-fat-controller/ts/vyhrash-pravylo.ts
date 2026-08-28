test("правило тримається без екрана", () => {
  const m = new Thermostat(29);
  m.nudge(+1);   // 30
  m.nudge(+1);   // спроба 31 → лишається 30
  m.nudge(+1);   // знову 30
  expect(m.target).toBe(30);           // верхня межа тримається — БЕЗ віджета
});

test("нижня межа тримається", () => {
  const m = new Thermostat(6);
  m.nudge(-1); m.nudge(-1); m.nudge(-1);
  expect(m.target).toBe(5);
});

test("обидва подання реагують на одну зміну", () => {
  const m = new Thermostat(22);
  const seen: Array<[string, number]> = [];
  m.onChange(() => seen.push(["подання-А", m.target]));
  m.onChange(() => seen.push(["подання-Б", m.target]));
  m.nudge(+1);
  expect(seen).toEqual([["подання-А", 23], ["подання-Б", 23]]);  // обидва почули
});

test("на межі зайвого сигналу нема", () => {
  const m = new Thermostat(30);
  const fired: number[] = [];
  m.onChange(() => fired.push(1));
  m.nudge(+1);                          // число не змінилось
  expect(fired).toEqual([]);
});
