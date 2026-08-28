// Фейкове членство для тесту: проста таблиця user → home → role.
class StaticMemberships implements Memberships {
  constructor(private readonly table: Record<string, Record<string, Role>>) {}
  async roleIn(userId: string, homeId: string): Promise<Role | undefined> {
    return this.table[userId]?.[homeId];   // немає запису → undefined → «не член»
  }
}

test("чужий мешканець не відчиняє чужий замок", async () => {
  const authz = new InServiceAuthorizer(new StaticMemberships({
    oksana: { "home-12": "resident" },     // Оксана — мешканка дому 12
    bohdan: { "home-7":  "resident" },     // Богдан — мешканець дому 7
  }));
  const door42 = { homeId: "home-7" };     // замок Богдана

  // ГОЛОВНИЙ ДОКАЗ: чужий мешканець на чужому замку — DENY.
  expect(await authz.can({ id: "oksana" }, "unlock", door42)).toBe(false);
  // Контроль: свій мешканець свій замок — можна.
  expect(await authz.can({ id: "bohdan" }, "unlock", door42)).toBe(true);
  // Відмова за замовчуванням: невідома дія — ні.
  expect(await authz.can({ id: "bohdan" }, "detonate" as Action, door42)).toBe(false);
  // Відмова за замовчуванням: узагалі не член жодного дому — ні.
  expect(await authz.can({ id: "stranger" }, "unlock", door42)).toBe(false);
});
