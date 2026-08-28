// — Керовані двійники: тест сам рухає час і сам відкликає членство —
class FakeClock { constructor(public t = 0) {} now = () => this.t; advance(ms: number) { this.t += ms; } }

class FakeStore implements RelationshipStore {              // центр зв'язків, кероване членство
  private members = new Set<string>();
  grant(u: string, h: string)  { this.members.add(`${u}:${h}`); }
  revoke(u: string, h: string) { this.members.delete(`${u}:${h}`); }  // ДЖЕРЕЛО ПРАВДИ оновлено
  async isMemberOf(u: string, h: string) { return this.members.has(`${u}:${h}`); }
}

class FixedPolicy implements PolicySource {                 // готове правило, без фонового тягання
  constructor(private p: Policy) {}
  policy() { return this.p; }
}

const BUNDLE: PolicyBundle = {
  version: "2026-07-12",
  actionsByRole: { owner: ["unlock","lock","view","configure"],
                   resident: ["unlock","lock","view"], guest: ["view"] },
  guestUnlock: { fromHour: 8, toHour: 22 },                 // гість відчиняє лише вдень
};
const at = (h: number) => h * HOUR;

test("push-інвалідація стискає вікно застарілості на відкликанні до ≈0", async () => {
  const guest: User    = { id: "guest7", roleInHome: { "home-7": "guest" } };
  const door:  Resource = { homeId: "home-7" };

  // ── Прогін 1: СТРАТЕГІЯ «лише TTL» ──
  const clock = new FakeClock(at(9));                        // 09:00 — у гостьовому вікні
  const store = new FakeStore(); store.grant("guest7", "home-7");
  const cache = new RelationshipCache(store, clock.now, 60_000, 5_000);
  const authz = new HybridAuthorizer(new FixedPolicy(compilePolicy(BUNDLE)), cache, clock.now);

  expect(await authz.can(guest, "unlock", door)).toBe(true);  // 1) тепло: член, у вікні → allow (кеш +)

  store.revoke("guest7", "home-7");                           // 2) відкликано В ЦЕНТРІ; кеш ще не знає
  clock.advance(5_000);                                       //    минуло 5 c — усе ще день

  expect(await authz.can(guest, "unlock", door)).toBe(true);  // 3a) кеш «член» → ВСЕ ЩЕ allow — ДІРА

  clock.advance(60_000);                                      //    дотягуємо час за TTL
  expect(await authz.can(guest, "unlock", door)).toBe(false); // 3b) кеш протух → центр → deny

  // ── Прогін 2: те саме, але з PUSH-ІНВАЛІДАЦІЄЮ на подію revoke ──
  const clk2 = new FakeClock(at(9));
  const st2 = new FakeStore(); st2.grant("guest7", "home-7");
  const cch2 = new RelationshipCache(st2, clk2.now, 60_000, 5_000);
  const az2 = new HybridAuthorizer(new FixedPolicy(compilePolicy(BUNDLE)), cch2, clk2.now);

  expect(await az2.can(guest, "unlock", door)).toBe(true);    // тепло, як і раніше

  st2.revoke("guest7", "home-7");                             // джерело правди оновлено…
  cch2.onRevoked("guest7", "home-7");                         // …і подія ОДРАЗУ чистить кеш
  clk2.advance(5_000);                                        // ті самі 5 c

  expect(await az2.can(guest, "unlock", door)).toBe(false);   // вікно ≈ 0: наступна ж перевірка → deny
});
