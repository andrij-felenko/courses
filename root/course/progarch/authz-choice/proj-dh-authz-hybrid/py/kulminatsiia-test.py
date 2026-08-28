import asyncio
from dataclasses import dataclass

class FakeClock:
    def __init__(self, t=0): self.t = t
    def now(self): return self.t
    def advance(self, ms): self.t += ms

class FakeStore:                                   # центр зв'язків, кероване членство
    def __init__(self): self._m = set()
    def grant(self, u, h):  self._m.add((u, h))
    def revoke(self, u, h): self._m.discard((u, h))    # ДЖЕРЕЛО ПРАВДИ оновлено
    async def is_member_of(self, u, h): return (u, h) in self._m

class FixedPolicy:                                 # готове правило, без фонового тягання
    def __init__(self, p): self._p = p
    def policy(self): return self._p

BUNDLE = PolicyBundle("2026-07-12",
    {"owner": ["unlock","lock","view","configure"],
     "resident": ["unlock","lock","view"], "guest": ["view"]},
    (8, 22))                                        # гість відчиняє лише вдень
at = lambda h: h * HOUR

@dataclass
class U:  id: str; role_in_home: dict
@dataclass
class Door: home_id: str

def test_push_invalidation_shrinks_revocation_window():
    async def scenario():
        guest = U("guest7", {"home-7": "guest"})
        door  = Door("home-7")

        # ── Прогін 1: СТРАТЕГІЯ «лише TTL» ──
        clock = FakeClock(at(9))                          # 09:00 — у гостьовому вікні
        store = FakeStore(); store.grant("guest7", "home-7")
        cache = RelationshipCache(store, clock.now, 60_000, 5_000)
        authz = HybridAuthorizer(FixedPolicy(compile_policy(BUNDLE)), cache, clock.now)

        assert await authz.can(guest, "unlock", door) is True    # 1) тепло → allow (кеш +)

        store.revoke("guest7", "home-7")                         # 2) відкликано В ЦЕНТРІ; кеш не знає
        clock.advance(5_000)                                     #    минуло 5 c

        assert await authz.can(guest, "unlock", door) is True    # 3a) кеш «член» → ВСЕ ЩЕ allow — ДІРА

        clock.advance(60_000)                                    #    за TTL
        assert await authz.can(guest, "unlock", door) is False   # 3b) кеш протух → центр → deny

        # ── Прогін 2: з PUSH-ІНВАЛІДАЦІЄЮ ──
        clk2 = FakeClock(at(9))
        st2 = FakeStore(); st2.grant("guest7", "home-7")
        cch2 = RelationshipCache(st2, clk2.now, 60_000, 5_000)
        az2 = HybridAuthorizer(FixedPolicy(compile_policy(BUNDLE)), cch2, clk2.now)

        assert await az2.can(guest, "unlock", door) is True      # тепло

        st2.revoke("guest7", "home-7")                           # джерело правди…
        cch2.on_revoked("guest7", "home-7")                      # …і подія ОДРАЗУ чистить кеш
        clk2.advance(5_000)

        assert await az2.can(guest, "unlock", door) is False     # вікно ≈ 0 → deny

    asyncio.run(scenario())
