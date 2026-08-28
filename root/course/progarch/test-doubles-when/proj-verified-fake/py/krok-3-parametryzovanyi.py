import pytest

# фабрика на кожну реалізацію — набір нижче про них нічого більше не знає
@pytest.fixture(params=[InMemoryStore, SqliteStore])
def store(request):
    return request.param()          # свіже сховище на КОЖНУ перевірку

def test_save_then_recent(store):
    store.save(Reading(1000, 20.0))
    assert store.recent(10) == [Reading(1000, 20.0)]

def test_recent_newest_first(store):
    for at in (3000, 1000, 2000):   # БЕЗЛАДНО
        store.save(Reading(at, at / 100))
    assert [r.at for r in store.recent(2)] == [3000, 2000]
