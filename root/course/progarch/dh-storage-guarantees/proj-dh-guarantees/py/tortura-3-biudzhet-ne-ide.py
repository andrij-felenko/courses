def _hammer_budget(path, home_id, tries):
    reg = open_registry(path)                     # свій конекшн у кожного процеса
    for _ in range(tries):
        try_consume_heat(reg, home_id, 1)         # UPDATE … WHERE heat_left >= 1

def test_budget_never_overspent(tmp_path):
    path = str(tmp_path / "dh.db")
    boot = open_registry(path)
    boot.execute("... CREATE TABLE homes ...")
    save_home(boot, {"id":"h1","owner":"ada","threshold":21.0,"heat_left":30,"devices":[]})
    boot.close()

    procs = [mp.Process(target=_hammer_budget, args=(path, "h1", 30)) for _ in range(8)]
    for p in procs: p.start()          # 8×30 = 240 спроб списати на бюджет у 30 хвилин
    for p in procs: p.join()

    reg  = open_registry(path)
    left = reg.execute("SELECT heat_left FROM homes WHERE id='h1'").fetchone()[0]
    assert left == 0        # 8 процесів разом випили РІВНО бюджет — ні хвилиною більше
    assert left >= 0        # і жодного разу не пірнули в мінус (інакше CHECK підняв би помилку)
