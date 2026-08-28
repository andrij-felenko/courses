// Фейковий, але МУТАБЕЛЬНИЙ граф — щоб змоделювати відкликання.
class FakeTuples implements TupleStore {
  constructor(
    private homes:   Record<string, string>,                // "door:42" → "home:7"
    private members: Record<string, Record<string, Role>>,  // "home:7" → { "user:bohdan": "resident" }
  ) {}
  async homeOf(object: string)               { return this.homes[object]; }
  async roleOf(home: string, subject: string) { return this.members[home]?.[subject]; }
}

test("центральний шлях: свій — так, чужий і підроблений контекст — ні, центр мовчить — ні", async () => {
  const members: Record<string, Record<string, Role>> = { "home:7": { "user:bohdan": "resident" } };
  const tuples  = new FakeTuples({ "door:42": "home:7" }, members);
  const cache   = new VerdictCache(new GraphPdp(tuples), 60_000, 60_000); // TTL навмисне ДОВГІ
  const authz   = new CentralAuthorizer(cache);

  const door42  = { kind: "door", id: "42", homeId: "home:7"  };
  const spoofed = { kind: "door", id: "42", homeId: "home:12" }; // Оксана «підклала» свій дім
  const bohdan  = { id: "bohdan" };
  const oksana  = { id: "oksana" };

  // 1) свій мешканець — можна (і це «можна» осідає в кеші)
  expect(await authz.can(bohdan, "unlock", door42)).toBe(true);
  // 2) чужий: Оксана не член дому 7 — DENY (IDOR закрито В ЦЕНТРІ)
  expect(await authz.can(oksana, "unlock", door42)).toBe(false);
  // 3) ПІДРОБЛЕНИЙ контекст не рятує: граф бере дім із КОРТЕЖА, а не з context.homeId
  expect(await authz.can(oksana, "unlock", spoofed)).toBe(false);
  // 4) центр мовчить → fail-closed
  const dead = new CentralAuthorizer({ check: async () => { throw new Error("pdp down"); } });
  expect(await dead.can(bohdan, "unlock", door42)).toBe(false);

  // 5) ВІДКЛИКАННЯ мусить бити ПОДІЄЮ, а не чекати TTL:
  delete members["home:7"]["user:bohdan"];              // домогосподарство виключило Богдана з графа
  // …але кеш іще тримає старе «можна» (TTL довгий) — і без події це діра:
  expect(await authz.can(bohdan, "unlock", door42)).toBe(true);   // ← НЕБЕЗПЕЧНО: несвіже «можна»
  cache.onRevoked("bohdan", "home:7");                  // ПОДІЯ чистить запис ОДРАЗУ
  expect(await authz.can(bohdan, "unlock", door42)).toBe(false);  // тепер центр каже «ні»
});
