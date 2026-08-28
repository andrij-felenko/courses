import pytest

@pytest.fixture(params=["file", "sqlite"])
def open_repo(request, tmp_path):
    """Повертає функцію, що ВІДКРИВАЄ репозиторій над тим самим шляхом.
    Покликати її двічі = два різні обʼєкти над одним сховищем."""
    def _open():
        if request.param == "file":
            return FileDeviceRepository(str(tmp_path / "dh-devices.json"))
        return SqliteDeviceRepository(str(tmp_path / "dh.db"))
    return _open

def test_registry_survives_restart(open_repo):
    repo = open_repo()
    repo.save(Device("lock-1", "lock", "вхідні двері"))
    repo.save(Device("plug-2", "plug", "кухня"))

    del repo                                    # ← «смерть процесу»: обʼєкт і вся його RAM зникли

    reborn = open_repo()                         # новий процес відкриває те саме сховище
    ids = {d.id for d in reborn.all()}
    assert ids == {"lock-1", "plug-2"}           # реєстр уцілів попід «рестартом»
    assert reborn.get("plug-2").room == "кухня"  # і поля на місці, не лише ключі
