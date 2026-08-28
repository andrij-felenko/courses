def test_registry_survives_restart(tmp_path):
    path = str(tmp_path / "dh.db")

    reg1 = connect(path, "FULL")                 # ── перший «запуск» ──
    run_migrations(reg1)
    SqliteDeviceRepository(reg1).save_home(Home(
        id="h1", owner_id="ada", plan="free", device_cap=5, threshold=21.0,
        devices=[Device("lock-1", "lock", "двері", "Locked", "2026-07-01T10:00"),
                 Device("plug-2", "plug", "кухня", "On",     "2026-07-01T10:05")]))
    reg1.close()                                 # ← процес помер: у памʼяті НІЧОГО не лишилось

    reg2 = connect(path, "FULL")                 # ── другий «запуск» над тим самим файлом ──
    assert run_migrations(reg2) == 2             # ідемпотентно: current=2, накочувати нема чого
    home = SqliteDeviceRepository(reg2).load("h1")

    assert home is not None                      # дім знайдено
    assert home.threshold == 21.0                # конфіг цілий
    assert {d.id for d in home.devices} == {"lock-1", "plug-2"}   # ← реєстр пережив рестарт
