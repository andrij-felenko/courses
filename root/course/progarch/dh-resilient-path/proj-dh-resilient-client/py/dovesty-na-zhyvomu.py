import asyncio


class FakeNet:
    def __init__(self):
        self.max_conc = {}
        self._live = {}
        self.telemetry_mode = "healthy"

    def transport_for(self, dep):
        async def transport(_addr, _path, _body):
            self._live[dep] = self._live.get(dep, 0) + 1
            self.max_conc[dep] = max(self.max_conc.get(dep, 0), self._live[dep])
            try:
                if dep == "telemetry" and self.telemetry_mode == "slow":
                    await asyncio.sleep(5.0)                    # висить 5 с; wait_for скасує на 3-й
                    return {"status": 200, "body": []}
                if dep == "telemetry" and self.telemetry_mode == "fail":
                    await asyncio.sleep(0.02); return {"status": 503, "body": None}
                await asyncio.sleep(0.02); return {"status": 200, "body": sample(dep)}
            finally:
                self._live[dep] -= 1
        return transport


async def test_degrade_and_isolate():
    net = FakeNet()
    net.telemetry_mode = "slow"                                # ← душимо телеметрію
    screens = [timed(main_screen(f"u{i}")) for i in range(50)]
    cmds = [lock_door(f"d{i}") for i in range(10)]
    tiles, cmd_res = await asyncio.gather(
        asyncio.gather(*screens),
        asyncio.gather(*cmds, return_exceptions=True),
    )
    # 1. Екран ДЕГРАДУВАВ, а не завис: пристрій є, reading = None.
    assert all(all(x["device"] and x["reading"] is None for x in t.value) for t in tiles)
    # 2. Телеметрія НЕ з'їла більше за свій пул; ядро качало вільно.
    assert net.max_conc["telemetry"] <= 10
    assert net.max_conc["core"] >= 40
    # 3. БІЛЬШІСТЬ екранів повернулись швидко (миттєвий «відсік повний» → фолбек).
    assert sum(1 for t in tiles if t.ms < 0.1) >= 40
    # 4. Усі команди пройшли — жодної брехні «зачинено».
    assert all(not isinstance(c, Exception) for c in cmd_res)
    print("деградація й ізоляція: OK", net.max_conc)
