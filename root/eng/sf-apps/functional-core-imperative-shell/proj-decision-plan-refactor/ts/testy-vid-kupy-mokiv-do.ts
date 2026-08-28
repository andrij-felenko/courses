// ── ДО: тест мусить обставити всі дотики до світу ──
test("over-limit flags and notifies", async () => {
  // 1. підробка бази з потрібним рахунком і шпигунами на записах
  const db = {
    loadAccount: async () => ({ id: "a1", userId: "u1",
                                balance: 500, dailyLimit: 100 }),
    flagTransaction: jest.fn(),
    freezeAccount:   jest.fn(),
    setBalance:      jest.fn(),
  };
  // 2. підробка сповіщувача
  const notifier = { push: jest.fn() };
  // 3. підробка журналу
  const audit = { log: jest.fn() };
  // 4. підмінити глобальні залежності на підробки (DI або monkey-patch)
  inject({ db, notifier, audit });

  await handleTransaction("a1", { id: "t1", amount: 150 });

  // 5. і тепер — допит шпигунів: покликали правильно?
  expect(db.flagTransaction).toHaveBeenCalledWith("t1", "over-limit");
  expect(notifier.push).toHaveBeenCalledWith("u1",
    "Транзакцію відкладено на перевірку");
});
