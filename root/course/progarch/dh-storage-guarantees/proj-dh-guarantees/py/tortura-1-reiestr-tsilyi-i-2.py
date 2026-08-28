def registry_is_whole(path, old, new) -> bool:
    reg = open_registry(path)
    row = reg.execute("SELECT threshold FROM homes WHERE id=?", (new["id"],)).fetchone()
    threshold = row[0] if row else None
    devs = {r[0] for r in reg.execute("SELECT id FROM devices WHERE home_id=?", (new["id"],))}
    is_old = threshold == old["threshold"] and devs == {d["id"] for d in old["devices"]}
    is_new = threshold == new["threshold"] and devs == {d["id"] for d in new["devices"]}
    return is_old or is_new         # третього стану бути НЕ СМІЄ

def test_registry_atomic_under_kill(tmp_path):
    path = str(tmp_path / "dh.db")
    boot = open_registry(path)
    boot.execute("... CREATE TABLE homes ...; ... CREATE TABLE devices ...")   # схема вище
    old = {"id":"h1","owner":"ada","threshold":21.0,"heat_left":30,
           "devices":[{"id":"lock-1","kind":"lock","room":"двері"}]}
    save_home(boot, old); boot.close()

    new = {"id":"h1","owner":"ada","threshold":24.0,"heat_left":30,
           "devices":[{"id":"lock-1","kind":"lock","room":"двері"},
                      {"id":"plug-2","kind":"plug","room":"кухня"}]}

    for _ in range(50):             # бʼємо багато разів — краш має бути безпечним ЩОРАЗУ
        kill_at_brink(_writer_home_before_commit, (path, new))
        assert registry_is_whole(path, old, new)                       # ніколи не піврозібраний
        reg = open_registry(path)
        assert reg.execute("PRAGMA integrity_check").fetchone()[0] == "ok"   # і не пошкоджений
        reg.close()
