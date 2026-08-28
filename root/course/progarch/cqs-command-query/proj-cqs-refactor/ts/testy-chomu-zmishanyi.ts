// КОМАНДА: перевіряємо НЕ повернене (його нема), а зміну стану — через запит
test("record — дописує показник у стан", () => {
  const svc = new EnergyService(250);
  expect(svc.readingCount("boiler")).toBe(0);

  const result = svc.record("boiler", 3);
  expect(result).toBeUndefined();               // команді нема чого повертати

  expect(svc.readingCount("boiler")).toBe(1);   // ефект видно лише запитом
  expect(svc.projectedBill("boiler")).toBe(750);
});
