def test_aggregate_lands_all_or_nothing(tmp_path):
    path = str(tmp_path / "dh.db")
    reg = connect(path, "FULL"); run_migrations(reg)
    repo = SqliteDeviceRepository(reg)

    repo.save_home(Home("h1", "ada", "free", 5, threshold=21.0,      # вихідний дім: поріг 21,
                        devices=[Device("lock-1", "lock", "двері", "Locked", "t0")]))  # один замок

    poisoned = Home("h1", "ada", "free", 5, threshold=24.0, devices=[  # намір: поріг 24 + два пристрої
        Device("plug-2", "plug", "кухня", "On", "t1"),                 # добрий — ляже перший…
        Device("bad-3", "???",  "гараж", "On", "t2")])                 # …а цей ЛАМАЄ CHECK(kind)

    with pytest.raises(sqlite3.IntegrityError):     # поганий пристрій підриває транзакцію
        repo.save_home(poisoned)

    survivor = repo.load("h1")                        # читаємо, ЩО лишилось на диску
    assert survivor.threshold == 21.0                 # ← поріг НЕ змінився: відкотилось усе
    assert {d.id for d in survivor.devices} == {"lock-1"}   # ← plug-2 теж зник, хоч ліг ДО поганого
