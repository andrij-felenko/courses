import asyncio, bisect
from dataclasses import dataclass, field

# Core — крихітне сильно-узгоджене KV (etcd / ZooKeeper / Chubby усередині).
# КОЖЕН його виклик = раунд до живої більшості, тож у гарячий шлях воно НЕ лізе.
class Core:                                        # інтерфейс: get / cas / watch
    async def get(self, key: str) -> tuple[str | None, int]: ...
    async def cas(self, key: str, val: str, expect_rev: int, ttl: float = 0) -> tuple[int, bool]: ...
    async def watch(self, key: str): ...           # async-генератор подій (val, rev)

# ── DATA PLANE — гарячий шлях. Локальний кеш shard-map → 0 раундів у ядро. ──
@dataclass
class ShardMap:
    hi: list[int] = field(default_factory=list)    # верхні межі діапазонів home_id
    shard: list[str] = field(default_factory=list) # shard[i] тримає діапазон, що кінчається на hi[i]
    epoch: int = 0                                  # ревізія ядра — fencing проти застарілого кешу

    def route(self, home_id: int) -> tuple[str, int]:
        i = bisect.bisect_left(self.hi, home_id)   # двійковий пошук у пам'яті: наносекунди
        return self.shard[i], self.epoch           # жодної мережі, жодного консенсусу

    async def refresh(self, core: Core):
        async for ev in core.watch("/dh/shard-map"):   # рідко: лише при ребалансі, не на запит
            self.hi, self.shard = parse_map(ev.val)    # парсер мапи опущено: тривіальний
            self.epoch = ev.rev

# ── CONTROL PLANE — ліза лідера нічних джоб. Раунд на здобуття + рідкі поновлення. ──
async def run_as_leader(core: Core, me: str, job, ttl: float = 10.0):
    key = "/dh/leader/night-jobs"
    while True:
        _, rev = await core.get(key)
        if rev == 0:                               # вакансія — пробуємо зайняти CAS-ом
            new_rev, ok = await core.cas(key, me, expect_rev=0, ttl=ttl)
            if ok:
                await _lead(core, key, me, new_rev, ttl, job)  # ми лідер
        await asyncio.sleep(ttl / 3)               # не лідер — зазираємо зрідка, не жаримо ядро

async def _lead(core, key, me, rev, ttl, job):
    task = asyncio.create_task(job())              # РОБОТА лідера (ребаланс) — локальна
    try:
        while True:
            await asyncio.sleep(ttl / 3)           # поновлюємо втричі частіше за строк
            rev, ok = await core.cas(key, me, expect_rev=rev, ttl=ttl)  # «я досі я»
            if not ok:
                return                             # втратили лізу — job спиниться у finally
    finally:
        task.cancel()
