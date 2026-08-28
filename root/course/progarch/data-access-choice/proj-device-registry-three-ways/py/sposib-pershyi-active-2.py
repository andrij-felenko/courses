import pytest

@pytest.mark.django_db          # ← без цього рядка тест НЕ запуститься
def test_save_then_find():
    d = Device.objects.create(type="lock", room="entrance", state="locked")
    same = Device.objects.get(pk=d.id)
    assert same.room  == "entrance"
    assert same.state == "locked"

@pytest.mark.django_db          # ← і тут теж — правило читає базу
def test_silent_are_found():
    Device.objects.create(type="lamp", room="hall", last_seen=None)
    Device.objects.create(type="lock", room="entrance", last_seen=9_000)
    silent = list(Device.objects.filter(last_seen__isnull=True))
    assert len(silent) == 1
