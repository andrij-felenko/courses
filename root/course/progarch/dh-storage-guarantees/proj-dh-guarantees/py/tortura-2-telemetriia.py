def _writer_flood(path, n_committed, brink):
    tel = open_telemetry(path)
    for i in range(1, n_committed + 1):
        tel.execute("BEGIN")
        tel.execute("INSERT INTO telemetry(device, ts, value) VALUES(?,?,?)",
                    ("sensor-1", float(i), 20.0 + i))
        tel.execute("COMMIT")           # закоміченy рядок: закритий, злитий у WAL
    tel.execute("BEGIN")                # відкриваємо (n+1)-й — і НЕ комітимо
    tel.execute("INSERT INTO telemetry(device, ts, value) VALUES(?,?,?)",
                ("sensor-1", 0.0, -999.0))          # ХВІСТ: його не має пережити kill
    brink.set()
    import time; time.sleep(3600)

def test_telemetry_loses_only_tail(tmp_path):
    path = str(tmp_path / "dh.db")
    open_telemetry(path).execute("... CREATE TABLE telemetry ...")
    kill_at_brink(_writer_flood, (path, 1000))

    tel = open_telemetry(path)
    n   = tel.execute("SELECT COUNT(*) FROM telemetry").fetchone()[0]
    poison = tel.execute("SELECT COUNT(*) FROM telemetry WHERE value = -999").fetchone()[0]
    assert n == 1000                    # усі 1000 ЗАКОМІЧЕНИХ рядків уціліли
    assert poison == 0                  # незакомічений хвіст зник — рівно як домовлялись
    assert tel.execute("PRAGMA integrity_check").fetchone()[0] == "ok"   # база ціла
