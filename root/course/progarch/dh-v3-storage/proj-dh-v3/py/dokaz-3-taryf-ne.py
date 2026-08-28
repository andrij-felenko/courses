import multiprocessing as mp

def _hammer_add(path, home_id, worker, tries):    # МУСИТЬ бути на верхньому рівні (spawn на Windows)
    repo = SqliteDeviceRepository(connect(path, "FULL"))   # свій конекшн у кожного процеса
    for i in range(tries):
        try:
            repo.add_device(home_id, Device(f"{worker}-{i}", "plug", "кімната", "On", "t"))
        except sqlite3.IntegrityError:
            pass                                   # рідкісний збіг id — не наша ціль тут

def test_tariff_never_exceeded_under_concurrency(tmp_path):
    path = str(tmp_path / "dh.db")
    boot = connect(path, "FULL"); run_migrations(boot)
    SqliteDeviceRepository(boot).save_home(
        Home("h1", "ada", "free", device_cap=5, threshold=20.0, devices=[]))   # 5 слотів, 0 зайнято
    boot.close()

    procs = [mp.Process(target=_hammer_add, args=(path, "h1", w, 20)) for w in range(8)]
    for p in procs: p.start()                      # 8×20 = 160 спроб на тариф у 5 слотів
    for p in procs: p.join()

    reg = connect(path, "FULL")
    used = reg.execute("SELECT used_slots FROM home WHERE id='h1'").fetchone()[0]
    rows = reg.execute("SELECT COUNT(*) FROM device WHERE home_id='h1'").fetchone()[0]
    assert used == 5                               # ← рівно тариф зайнято, ні слотом більше
    assert rows == 5                               # ← і рівно 5 пристроїв на диску: лічильник = реальність
